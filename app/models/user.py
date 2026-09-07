from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_image_path = Column(String(500), nullable=True)
    role = Column(String(50), nullable=False, default="customer")
    is_verified = Column(Boolean, nullable=False, default=False)
    otp = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)