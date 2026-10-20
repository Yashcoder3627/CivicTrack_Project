from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="citizen", nullable=False)   # citizen / officer / admin



class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(String(20), default="Pending", nullable=False)  # Pending / In Progress / Resolved
    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)       # kisne complaint ki (citizen)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)    # kis officer ko di gayi (shuru mein khali)
    image_path = Column(String(255), nullable=True)    # uploaded photo ka file naam (ya khali)