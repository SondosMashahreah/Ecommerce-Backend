from sqlalchemy.orm import Session

from app.models.favorite import Favorite


def add_to_favorites(
    db: Session,
    user_id: int,
    product_id: int
):
    existing_favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        )
        .first()
    )

    if existing_favorite:
        return existing_favorite

    favorite = Favorite(
        user_id=user_id,
        product_id=product_id
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


def get_favorites(
    db: Session,
    user_id: int
):
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id)
        .all()
    )


def remove_from_favorites(
    db: Session,
    user_id: int,
    favorite_id: int
):
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.id == favorite_id,
            Favorite.user_id == user_id
        )
        .first()
    )

    if not favorite:
        return None

    db.delete(favorite)
    db.commit()

    return favorite