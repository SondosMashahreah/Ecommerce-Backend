from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.core.admin import get_current_admin
from app.db.database import get_db
from app.models.rating import Rating
from app.models.user import User
from app.models.product import Product

router = APIRouter(prefix="/admin/reviews", tags=["Admin Reviews"],
                   dependencies=[Depends(get_current_admin)])


@router.get("/")
def list_reviews(search: str = "", stars: int | None = Query(default=None, ge=1, le=5),
                 page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    query = db.query(Rating, User.username, Product.name).join(User, Rating.user_id == User.id).join(Product, Rating.product_id == Product.id)
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.username.ilike(term), Product.name.ilike(term), Rating.comment.ilike(term)))
    if stars is not None:
        query = query.filter(Rating.rating == stars)
    total = query.count()
    average = query.with_entities(func.avg(Rating.rating)).scalar() or 0
    rows = query.order_by(Rating.id.desc()).offset((page - 1) * 25).limit(25).all()
    return {"total": total, "average": round(float(average), 1), "page": page, "page_size": 25,
            "items": [{"id": rating.id, "product_id": rating.product_id, "product_name": product,
                       "user_name": username, "rating": rating.rating, "comment": rating.comment}
                      for rating, username, product in rows]}
