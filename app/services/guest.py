"""Anonymous customer sessions using the existing user and shopping tables."""
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password
from app.models.cart import CartItem
from app.models.favorite import Favorite
from app.models.order import Order
from app.models.rating import Rating
from app.models.user import User


def guest_tokens(user: User):
    return {
        "access_token": create_access_token(user.id, guest=True),
        "refresh_token": create_refresh_token(user.id, guest=True),
        "token_type": "bearer",
    }


def create_guest(db: Session):
    identifier = secrets.token_hex(16)
    user = User(
        name="Guest",
        username=f"guest_{identifier}",
        email=f"{identifier}@guest.example.com",
        password_hash=hash_password(secrets.token_urlsafe(48)),
        role="guest",
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return guest_tokens(user)


def merge_guest(db: Session, current_user: User, refresh_token: str):
    """Consume a guest session once, retaining reserved stock and order snapshots."""
    if current_user.role not in {"customer", "admin"} or not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Sign in to merge your guest session")
    payload = decode_refresh_token(refresh_token)
    if not payload or payload.get("type") != "guest_refresh" or not str(payload.get("sub", "")).isdigit():
        raise HTTPException(status_code=401, detail="Invalid guest session")

    guest_id = int(payload["sub"])
    # Lock both owners in a stable order so concurrent retries cannot duplicate a cart.
    users = db.query(User).filter(User.id.in_([guest_id, current_user.id])).order_by(User.id).with_for_update().all()
    guest = next((user for user in users if user.id == guest_id), None)
    if not guest or guest.role != "guest":
        raise HTTPException(status_code=401, detail="Invalid guest session")
    if not guest.is_active:
        return {"merged": True}  # A previous successful attempt already consumed it.

    try:
        own_cart = {item.product_item_id: item for item in db.query(CartItem).filter(CartItem.user_id == current_user.id).all()}
        for item in db.query(CartItem).filter(CartItem.user_id == guest.id).all():
            existing = own_cart.get(item.product_item_id)
            if existing:
                existing.quantity += item.quantity
                db.delete(item)
            else:
                item.user_id = current_user.id
                own_cart[item.product_item_id] = item
        # Ownership changes do not reserve stock a second time.
        for model in (Favorite, Rating):
            own_products = {item.product_id for item in db.query(model).filter(model.user_id == current_user.id).all()}
            for item in db.query(model).filter(model.user_id == guest.id).all():
                if item.product_id in own_products:
                    db.delete(item)
                else:
                    item.user_id = current_user.id
                    own_products.add(item.product_id)
        db.query(Order).filter(Order.user_id == guest.id).update({Order.user_id: current_user.id})
        guest.is_active = False
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"merged": True}
