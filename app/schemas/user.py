from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


class UserSignup(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$"
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    profile_image_path: str | None = None
    role: str
    is_verified: bool

    model_config = {
        "from_attributes": True
    }


class UpdateProfileRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$"
    )


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=6,
        max_length=100
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str