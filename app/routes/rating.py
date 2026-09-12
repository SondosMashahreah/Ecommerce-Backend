from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    ProductRatingSummary
)
from app.services.rating import (
    rate_product,
    get_product_rating,
    get_user_product_rating
)


router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)


@router.post(
    "/",
    response_model=RatingResponse
)
def create_or_update_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return rate_product(
        db=db,
        user_id=current_user.id,
        product_id=data.product_id,
        rating_value=data.rating
    )


@router.get(
    "/product/{product_id}",
    response_model=ProductRatingSummary
)
def product_rating_summary(
    product_id: int,
    db: Session = Depends(get_db)
):
    return get_product_rating(
        db,
        product_id
    )


@router.get(
    "/me/{product_id}",
    response_model=RatingResponse | None
)
def my_product_rating(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_product_rating(
        db,
        current_user.id,
        product_id
    )
