from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.coupon import Coupon


def calculate_coupon(db: Session, code: str, subtotal: float):
    normalized_code = code.strip().upper()
    coupon = db.query(Coupon).filter(Coupon.code == normalized_code).first()
    if not coupon or not coupon.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive coupon code")

    amount = Decimal(str(subtotal))
    if not amount.is_finite() or amount <= 0:
        raise HTTPException(status_code=400, detail="Subtotal must be positive")
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount < coupon.minimum_order:
        raise HTTPException(status_code=400, detail=f"Minimum order is ${coupon.minimum_order:.2f}")

    discount = (amount * coupon.discount_value / 100
                if coupon.discount_type == "percent" else coupon.discount_value)
    discount = min(amount, discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {
        "code": normalized_code,
        "discount_percent": float(coupon.discount_value) if coupon.discount_type == "percent" else 0,
        "discount_amount": float(discount),
        "total": float(amount - discount),
    }
