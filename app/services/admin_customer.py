from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User


def get_admin_customers(
    db: Session,
    search: str | None = None,
):
    query = db.query(User)

    if search:
        pattern = f"%{search.strip()}%"

        query = query.filter(
            or_(
                User.name.ilike(pattern),
                User.username.ilike(
                    pattern
                ),
                User.email.ilike(pattern),
            )
        )

    return (
        query
        .order_by(
            User.created_at.desc()
        )
        .all()
    )


def get_admin_customer(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_customer_status(
    db: Session,
    user: User,
    is_active: bool,
):
    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


def update_customer_role(
    db: Session,
    user: User,
    role: str,
):
    if user.role == "guest":
        raise HTTPException(status_code=400, detail="Guest accounts cannot be promoted.")
    user.role = role

    db.commit()
    db.refresh(user)

    return user
