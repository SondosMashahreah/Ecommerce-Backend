from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import (UserSignup, UserResponse, VerifyOTP, UserLogin, TokenResponse)
from app.services.auth import (
    create_user,
    verify_user_otp,
    authenticate_user
)
from app.core.security import create_access_token, decode_access_token
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    return create_user(db, user_data)


@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    user = verify_user_otp(db, data)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return user


@router.post("/signin", response_model=TokenResponse)
def signin(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email, password, or unverified account"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    user = create_user(db, user_data)

    if not user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    return user