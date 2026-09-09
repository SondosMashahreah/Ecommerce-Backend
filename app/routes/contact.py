from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.contact import ContactMessage
from app.services.contact import (
    create_contact_message,
)


router = APIRouter()


@router.post("/contact")
def receive_contact(
    contact: ContactMessage,
    db: Session = Depends(get_db),
):
    new_contact = create_contact_message(
        db=db,
        data=contact,
    )

    return {
        "message":
            "Message saved successfully!",
        "id": new_contact.id,
    }