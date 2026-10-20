from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import database_models
from auth import (create_token, get_current_user, hash_password,
                  require_admin, require_staff, verify_password)
from database import engine, get_db
from database_models import Complaint, User
from schemas import (AssignUpdate, Category, ComplaintCreate, ComplaintOut, StatusUpdate,
                     Token, UserCreate, UserLogin, UserOut)
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import File, Form, UploadFile
from fastapi.staticfiles import StaticFiles

# Tables nahi hain toh bana deta hai
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CivicTrack")

# Frontend (browser) ko backend se baat karne ki ijazat
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500", "http://127.0.0.1:5500",
        "http://localhost:5501", "http://127.0.0.1:5501",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------- Photo upload ka setup ----------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")   # photo ka URL: /uploads/<naam>

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_PHOTO_BYTES = 2 * 1024 * 1024      # 2 MB

# =============== 1. Signup ===============
@app.post("/auth/signup", response_model=UserOut, status_code=201)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered")

    user = User(
        email=email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),   # plain password kabhi save nahi hota
        role="citizen",                                  # signup se hamesha citizen
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# =============== 2. Login ===============
@app.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return Token(access_token=create_token(user), role=user.role, name=user.full_name)


# =============== 3. Complaints dekhna ===============
# Citizen ko sirf apni, officer ko sirf apne ko assign hui, admin ko sabki.
@app.get("/complaints", response_model=List[ComplaintOut])
def list_complaints(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Complaint)
    if user.role == "citizen":
        query = query.filter(Complaint.user_id == user.id)
    elif user.role == "officer":
        query = query.filter(Complaint.assigned_to == user.id)
    return query.order_by(Complaint.id.desc()).all()


# =============== 4. Nayi complaint ===============
@app.post("/complaints", response_model=ComplaintOut, status_code=201)
def create_complaint(
    title: str = Form(..., min_length=3, max_length=150),
    category: Category = Form(...),
    description: str = Form(..., min_length=3),
    location: str = Form(..., min_length=2, max_length=255),
    photo: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_name = None
    if photo is not None and photo.filename:
        ext = ALLOWED_TYPES.get(photo.content_type)
        if ext is None:
            raise HTTPException(status_code=400, detail="Only JPG, PNG or WEBP photos are allowed")
        data = photo.file.read(MAX_PHOTO_BYTES + 1)
        if len(data) > MAX_PHOTO_BYTES:
            raise HTTPException(status_code=413, detail="Photo must be 2 MB or smaller")
        image_name = uuid.uuid4().hex + ext            # random naam: user ka diya naam kabhi use nahi hota
        (UPLOAD_DIR / image_name).write_bytes(data)

    complaint = Complaint(
        title=title,
        category=category.value,
        description=description,
        location=location,
        image_path=image_name,
        user_id=user.id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


# =============== 5. Status badalna (admin: koi bhi, officer: sirf apni) ===============
@app.patch("/complaints/{complaint_id}/status", response_model=ComplaintOut)
def update_status(
    complaint_id: int,
    data: StatusUpdate,
    staff: User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if staff.role == "officer" and complaint.assigned_to != staff.id:
        raise HTTPException(status_code=403, detail="This complaint is not assigned to you")
    complaint.status = data.status.value
    db.commit()
    db.refresh(complaint)
    return complaint


# =============== 6. Officers ki list (sirf admin) ===============
@app.get("/officers", response_model=List[UserOut])
def list_officers(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "officer").order_by(User.id).all()


# =============== 7. Naya officer banana (sirf admin) ===============
@app.post("/officers", response_model=UserOut, status_code=201)
def create_officer(data: UserCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered")
    officer = User(
        email=email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role="officer",
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)
    return officer


# =============== 8. Complaint officer ko assign karna (sirf admin) ===============
@app.patch("/complaints/{complaint_id}/assign", response_model=ComplaintOut)
def assign_complaint(
    complaint_id: int,
    data: AssignUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    officer = db.get(User, data.officer_id)
    if officer is None or officer.role != "officer":
        raise HTTPException(status_code=404, detail="Officer not found")
    complaint.assigned_to = officer.id
    db.commit()
    db.refresh(complaint)
    return complaint
