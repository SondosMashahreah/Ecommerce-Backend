from fastapi import APIRouter, Depends

from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.coupon import CouponRequest, CouponResponse
from app.services.coupon import calculate_coupon


router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.post("/validate", response_model=CouponResponse)
def validate_coupon(
    data: CouponRequest,
    current_user: User = Depends(get_current_user),
):
    return calculate_coupon(data.code, data.subtotal)
