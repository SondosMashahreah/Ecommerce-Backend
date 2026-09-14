from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.admin import get_current_admin
from app.db.database import get_db
from app.models.coupon import Coupon
from app.schemas.admin_coupon import AdminCouponResponse, CouponWrite

router = APIRouter(prefix="/admin/coupons", tags=["Admin Coupons"],
                   dependencies=[Depends(get_current_admin)])


@router.get("/", response_model=list[AdminCouponResponse])
def list_coupons(db: Session = Depends(get_db)):
    return db.query(Coupon).order_by(Coupon.id.desc()).all()


def save_coupon(db, coupon):
    try:
        db.add(coupon)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A coupon with this code already exists")
    db.refresh(coupon)
    return coupon


@router.post("/", response_model=AdminCouponResponse, status_code=201)
def create_coupon(data: CouponWrite, db: Session = Depends(get_db)):
    return save_coupon(db, Coupon(**data.model_dump()))


@router.put("/{coupon_id}", response_model=AdminCouponResponse)
def update_coupon(coupon_id: int, data: CouponWrite, db: Session = Depends(get_db)):
    coupon = db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    for field, value in data.model_dump().items():
        setattr(coupon, field, value)
    return save_coupon(db, coupon)
