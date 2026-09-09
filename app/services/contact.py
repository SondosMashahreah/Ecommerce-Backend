from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactMessage


def create_contact_message(
    db: Session,
    data: ContactMessage,
):
    contact = Contact(
        name=data.name,
        email=data.email,
        subject=data.subject,
        message=data.message,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact