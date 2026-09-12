from pydantic import BaseModel


class ContactMessage(BaseModel):
    name: str
    email: str
    subject: str
    message: str
