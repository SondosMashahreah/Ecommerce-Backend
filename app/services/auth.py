from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    UserSignup,
    VerifyOTP,
    UserLogin,
    UpdateProfileRequest,
    ChangePasswordRequest
)

from app.services.otp import generate_otp, get_otp_expiry
from app.services.email import send_otp_email


def create_user(
    db: Session,
    user_data: UserSignup
):
    email = user_data.email.strip().lower()
    username = user_data.username.strip().lower()
    name = user_data.name.strip()

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        return {
            "error": "email_exists"
        }

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        return {
            "error": "username_exists"
        }

    otp_code = generate_otp()

    new_user = User(
        name=name,
        username=username,
        email=email,
        password_hash=hash_password(
            user_data.password
        ),
        role="customer",
        is_verified=False,
        otp=otp_code,
        otp_expires_at=get_otp_expiry(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_otp_email(
        new_user.email,
        otp_code
    )

    return {
        "user": new_user
    }


def verify_user_otp(
    db: Session,
    data: VerifyOTP
):
    user = (
        db.query(User)
        .filter(
            User.email ==
            data.email.strip().lower()
        )
        .first()
    )

    if not user:
        return None

    if user.is_verified:
        return None

    if user.otp != data.otp:
        return None

    if not user.otp_expires_at:
        return None

    if (
        user.otp_expires_at
        < datetime.utcnow()
    ):
        return None

    user.is_verified = True
    user.otp = None
    user.otp_expires_at = None

    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    data: UserLogin
):
    email = data.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not user.is_verified:
        return None

    if not verify_password(
        data.password,
        user.password_hash
    ):
        return None

    return user


def update_user_profile(
    db: Session,
    current_user: User,
    data: UpdateProfileRequest
):
    name = data.name.strip()
    username = data.username.strip().lower()

    existing_username = (
        db.query(User)
        .filter(
            User.username == username,
            User.id != current_user.id
        )
        .first()
    )

    if existing_username:
        return {
            "error": "username_exists"
        }

    current_user.name = name
    current_user.username = username

    db.commit()
    db.refresh(current_user)

    return {
        "user": current_user
    }

def change_user_password(
    db: Session,
    current_user: User,
    data: ChangePasswordRequest
):
    password_is_correct = verify_password(
        data.current_password,
        current_user.password_hash
    )

    if not password_is_correct:
        return {
            "error": "incorrect_password"
        }

    same_password = verify_password(
        data.new_password,
        current_user.password_hash
    )

    if same_password:
        return {
            "error": "same_password"
        }

    current_user.password_hash = hash_password(
        data.new_password
    )

    db.commit()
    db.refresh(current_user)

    return {
        "success": True
    }