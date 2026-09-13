from pydantic import BaseModel, Field


class CouponRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    subtotal: float = Field(gt=0)


class CouponResponse(BaseModel):
    code: str
    discount_percent: float
    discount_amount: float
    total: float
