from fastapi import APIRouter

from app.db.database import SessionLocal
from app.models.contact import Contact
from app.schemas.contact import ContactMessage


router = APIRouter()


@router.post("/contact")
def receive_contact(contact: ContactMessage):

    db = SessionLocal()

    new_contact = Contact(
        name=contact.name,
        email=contact.email,
        subject=contact.subject,
        message=contact.message
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    db.close()

    return {
        "message": "Message saved successfully!",
        "id": new_contact.id
    }