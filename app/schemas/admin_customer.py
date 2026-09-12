from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
)


class AdminCustomerResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    profile_image_path: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AdminCustomerStatusUpdate(
    BaseModel
):
    is_active: bool


class AdminCustomerRoleUpdate(
    BaseModel
):
    role: Literal[
        "customer",
        "admin",
    ]
