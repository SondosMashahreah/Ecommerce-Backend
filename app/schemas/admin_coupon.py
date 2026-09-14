from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CouponWrite(BaseModel):
    code: str = Field(min_length=1, max_length=50, pattern=r"^[A-Z0-9_-]+$")
    discount_type: Literal["percent", "fixed"]
    discount_value: Decimal = Field(gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    minimum_order: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False)
    is_active: bool = True

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def valid_percentage(self):
        if self.discount_type == "percent" and self.discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        return self


class AdminCouponResponse(CouponWrite):
    model_config = ConfigDict(from_attributes=True)
    id: int
