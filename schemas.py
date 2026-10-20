from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Allowed values ----------
class Category(str, Enum):
    roads = "Roads"
    water = "Water"
    sanitation = "Sanitation"
    electricity = "Electricity"


class Status(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    resolved = "Resolved"


# ---------- Signup / Login ----------
class UserCreate(BaseModel):            # signup: user kya bhejta hai (role nahi, hamesha citizen)
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):             # login: user kya bhejta hai
    email: EmailStr
    password: str


class UserOut(BaseModel):               # server user ko kya dikhata hai (password kabhi nahi)
    id: int
    email: EmailStr
    full_name: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):                 # login ke baad server kya deta hai
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str


# ---------- Complaints ----------
class ComplaintCreate(BaseModel):       # citizen kya bhejta hai (user_id aur status nahi)
    title: str = Field(min_length=3, max_length=150)
    category: Category
    description: str = Field(min_length=3)
    location: str = Field(min_length=2, max_length=255)


class ComplaintOut(BaseModel):          # server complaint ke baare mein kya deta hai
    id: int
    title: str
    category: str
    description: str
    location: str
    status: str
    user_id: int
    assigned_to: Optional[int] = None      # officer ki id (ya khali)
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):          # admin status badalte waqt
    status: Status


class AssignUpdate(BaseModel):          # admin complaint kis officer ko de raha hai
    officer_id: int
