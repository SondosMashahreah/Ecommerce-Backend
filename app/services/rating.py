from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.rating import Rating


def rate_product(
    db: Session,
    user_id: int,
    product_id: int,
    rating_value: int
):
    existing_rating = (
        db.query(Rating)
        .filter(
            Rating.user_id == user_id,
            Rating.product_id == product_id
        )
        .first()
    )

    if existing_rating:
        existing_rating.rating = rating_value

        db.commit()
        db.refresh(existing_rating)

        return existing_rating

    new_rating = Rating(
        user_id=user_id,
        product_id=product_id,
        rating=rating_value
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating


def get_product_rating(
    db: Session,
    product_id: int
):
    result = (
        db.query(
            func.avg(Rating.rating),
            func.count(Rating.id)
        )
        .filter(
            Rating.product_id == product_id
        )
        .first()
    )

    average = result[0] or 0
    count = result[1] or 0

    return {
        "average_rating": round(float(average), 1),
        "ratings_count": count
    }


def get_user_product_rating(
    db: Session,
    user_id: int,
    product_id: int
):
    return (
        db.query(Rating)
        .filter(
            Rating.user_id == user_id,
            Rating.product_id == product_id
        )
        .first()
    )
