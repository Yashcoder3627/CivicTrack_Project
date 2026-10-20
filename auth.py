"""Password hashing + JWT login + "kaun logged in hai" ka check."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from database_models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")          # .env se aati hai, code mein kabhi nahi likhna
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY nahi mili. .env file mein SECRET_KEY=... jodo (SETUP.md dekho).")

ALGORITHM = "HS256"
TOKEN_HOURS = 8


# ---------- Password ----------
# bcrypt sirf pehle 72 bytes padhta hai, isliye dono jagah same kaat rahe hain.
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))


# ---------- JWT token ----------
def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),                                   # token kis user ka hai
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),   # kab expire hoga
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------- Request mein se logged-in user nikalna ----------
bearer = HTTPBearer(auto_error=False)      # header: Authorization: Bearer <token>


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Please log in first")
    try:
        data = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------- Role checks ----------
def require_staff(user: User = Depends(get_current_user)) -> User:
    """Admin ya officer."""
    if user.role not in ("admin", "officer"):
        raise HTTPException(status_code=403, detail="Only admin or officer can do this")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Sirf admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can do this")
    return user
