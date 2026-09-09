from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.contact import Contact


def get_admin_messages(
    db: Session,
    search: str | None = None,
    unread_only: bool = False,
):
    query = db.query(Contact)

    if unread_only:
        query = query.filter(
            Contact.is_read.is_(False)
        )

    if search:
        pattern = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Contact.name.ilike(
                    pattern
                ),
                Contact.email.ilike(
                    pattern
                ),
                Contact.subject.ilike(
                    pattern
                ),
                Contact.message.ilike(
                    pattern
                ),
            )
        )

    return (
        query
        .order_by(
            Contact.created_at.desc()
        )
        .all()
    )


def get_admin_message(
    db: Session,
    message_id: int,
):
    return (
        db.query(Contact)
        .filter(
            Contact.id == message_id
        )
        .first()
    )


def mark_message_read(
    db: Session,
    message: Contact,
):
    message.is_read = True

    db.commit()
    db.refresh(message)

    return message


def delete_message(
    db: Session,
    message: Contact,
):
    db.delete(message)
    db.commit()