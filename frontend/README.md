# CivicTrack: simple frontend (3 pages)

| File | Kaam |
|---|---|
| index.html | Login + Signup |
| citizen.html | Citizen: apni complaints dekho, nayi complaint daalo |
| officer.html | Officer: sirf apne ko assign hui complaints, status badlo |
| admin.html | Admin: sab complaints, officer ko assign karo, officer banao, status badlo |
| js/api.js | Backend se baat karne ka saara code (5 endpoints) |
| css/style.css | Design |

## Chalane ka tareeka

```
cd civictrack-simple
python -m http.server 5500
```
Browser mein http://localhost:5500 kholo (ya VS Code mein index.html par Live Server).
Backend alag terminal mein: `uvicorn main:app --reload` (http://127.0.0.1:8000).

## Backend mein CORS lagana zaroori hai

Bina iske browser backend ko block kar deta hai. `main.py` mein `app = FastAPI()` ke baad:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500",
                   "http://localhost:5501", "http://127.0.0.1:5501"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Backend ke 5 endpoints (ek ek karke banao, har ek ke baad page se test karo)

| Step | Backend endpoint | Frontend mein kahan dikhega |
|---|---|---|
| A | POST /auth/signup  body `{full_name, email, password}` | index.html, "Create an account" |
| B | POST /auth/login  body `{email, password}`, wapas `{access_token, role, name}` | index.html, "Sign in" |
| C | GET /complaints  (citizen ko apni, officer ko assigned, admin ko sab) | citizen.html ki list, admin.html ki table |
| D | POST /complaints  body `{title, category, description, location}` | citizen.html ka form |
| E | PATCH /complaints/{id}/status  body `{status}` (admin: koi bhi, officer: sirf assigned) | admin.html / officer.html ka Save button |
| F | GET /officers (sirf admin) | admin.html ka officer dropdown |
| G | POST /officers (sirf admin) | admin.html ka Add an officer form |
| H | PATCH /complaints/{id}/assign  body `{officer_id}` (sirf admin) | admin.html ka Assign button |

Complaint ke response mein ye fields chahiye: `id, title, category, description, location, status, user_id`.
`created_at` ho toh date bhi dikhegi (optional).
`status` ki values bilkul ye: `Pending`, `In Progress`, `Resolved`.

Admin ka account signup se nahi banta: MySQL mein apni email ka `role` `admin` kar do. Officer admin page ke "Add an officer" form se banta hai.

## Kuch gadbad ho toh kaise dhundhein

1. Browser mein `F12` dabao, phir **Network** tab kholo.
2. Page par koi button dabao. Har request ek line banke dikhegi.
3. Line par click karo: **Payload** (frontend ne kya bheja) aur **Response** (backend ne kya bheja) dikhega.
4. Red line = error. Status code dekho: 404 = endpoint nahi mila, 422 = bheja hua data schema se match nahi hua, 401 = token galat, 500 = backend ke code mein error (uvicorn ka terminal dekho).
5. **Console** tab mein JavaScript ke error dikhte hain.
