from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserSignup, VerifyOTP, UserLogin
from app.services.otp import generate_otp, get_otp_expiry
from app.services.email import send_otp_email


def create_user(db: Session, user_data: UserSignup):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        return None

    otp_code = generate_otp()

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="customer",
        is_verified=False,
        otp=otp_code,
        otp_expires_at=get_otp_expiry(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_otp_email(new_user.email, otp_code)

    return new_user


def verify_user_otp(db: Session, data: VerifyOTP):
    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        return None

    if user.is_verified:
        return None

    if user.otp != data.otp:
        return None

    if not user.otp_expires_at:
        return None

    if user.otp_expires_at < datetime.utcnow():
        return None

    user.is_verified = True
    user.otp = None
    user.otp_expires_at = None

    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, data: UserLogin):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        return None

    if not user.is_verified:
        return None

    if not verify_password(data.password, user.password_hash):
        return None

    return user