from fastapi import HTTPException


COUPONS = {
    "SAVE10": {"percent": 10, "minimum": 50},
    "WELCOME20": {"percent": 20, "minimum": 100},
}


def calculate_coupon(code: str, subtotal: float):
    normalized_code = code.strip().upper()
    coupon = COUPONS.get(normalized_code)

    if not coupon:
        raise HTTPException(status_code=400, detail="Invalid coupon code")

    if subtotal < coupon["minimum"]:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum order is ${coupon['minimum']}",
        )

    discount = round(subtotal * coupon["percent"] / 100, 2)
    return {
        "code": normalized_code,
        "discount_percent": coupon["percent"],
        "discount_amount": discount,
        "total": round(subtotal - discount, 2),
    }
