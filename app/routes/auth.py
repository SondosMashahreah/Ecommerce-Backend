from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile
)
from app.services.minio_service import upload_file

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.user import (
    UserSignup,
    UserResponse,
    VerifyOTP,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UpdateProfileRequest,
     ChangePasswordRequest
)

from app.services.auth import (
    create_user,
    verify_user_otp,
    authenticate_user,
    update_user_profile,
    change_user_password
)

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token
)

from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

security = HTTPBearer()


def get_current_user(
    credentials:
    HTTPAuthorizationCredentials =
    Depends(security),

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

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@router.post(
    "/signup",
    response_model=UserResponse
)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    result = create_user(
        db,
        user_data
    )

    if (
        result.get("error")
        == "email_exists"
    ):
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    if (
        result.get("error")
        == "username_exists"
    ):
        raise HTTPException(
            status_code=409,
            detail="Username already taken"
        )

    return result["user"]


@router.post(
    "/verify-otp",
    response_model=UserResponse
)
def verify_otp(
    data: VerifyOTP,
    db: Session = Depends(get_db)
):
    user = verify_user_otp(
        db,
        data
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return user


@router.post(
    "/signin",
    response_model=TokenResponse
)
def signin(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        data
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email, password, "
                "or unverified account"
            )
        )

    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="Account is disabled",
    )

    access_token = (
        create_access_token(
            user.id
        )
    )

    refresh_token = (
        create_refresh_token(
            user.id
        )
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user:
    User = Depends(get_current_user)
):
    return current_user


@router.patch(
    "/profile",
    response_model=UserResponse
)
def update_profile(
    data: UpdateProfileRequest,

    current_user:
    User = Depends(get_current_user),

    db: Session = Depends(get_db)
):
    result = update_user_profile(
        db,
        current_user,
        data
    )

    if (
        result.get("error")
        == "username_exists"
    ):
        raise HTTPException(
            status_code=409,
            detail="Username already taken"
        )

    return result["user"]

@router.patch("/password")
def change_password(
    data: ChangePasswordRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    result = change_user_password(
        db,
        current_user,
        data
    )

    if (
        result.get("error")
        == "incorrect_password"
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    if (
        result.get("error")
        == "same_password"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "New password must be different "
                "from current password"
            )
        )

    return {
        "message":
        "Password changed successfully"
    }

@router.post(
    "/profile/image",
    response_model=UserResponse
)
def upload_profile_image(
    file: UploadFile = File(...),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, PNG and WEBP "
                "images are allowed"
            )
        )

    file_path = upload_file(
        file,
        folder="users/profile-images"
    )

    current_user.profile_image_path = (
        file_path
    )

    db.commit()
    db.refresh(current_user)

    return current_user

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    payload = decode_refresh_token(
        data.refresh_token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or expired "
                "refresh token"
            )
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="Account is disabled",
    )

    new_access_token = (
        create_access_token(
            user.id
        )
    )

    new_refresh_token = (
        create_refresh_token(
            user.id
        )
    )

    return {
        "access_token":
        new_access_token,

        "refresh_token":
        new_refresh_token,

        "token_type":
        "bearer"
    }