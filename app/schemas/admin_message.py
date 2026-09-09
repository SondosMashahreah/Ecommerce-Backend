from datetime import datetime

from pydantic import BaseModel


class AdminMessageResponse(
    BaseModel
):
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }