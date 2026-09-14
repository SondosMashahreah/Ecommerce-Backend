from sqlalchemy import Boolean, CheckConstraint, Column, Integer, Numeric, String, text
from app.db.database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    discount_type = Column(String(10), nullable=False)
    discount_value = Column(Numeric(12, 2), nullable=False)
    minimum_order = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    __table_args__ = (
        CheckConstraint("discount_type IN ('percent', 'fixed')", name="ck_coupon_type"),
        CheckConstraint("discount_value > 0", name="ck_coupon_positive"),
        CheckConstraint("discount_type != 'percent' OR discount_value <= 100", name="ck_coupon_percent"),
        CheckConstraint("minimum_order >= 0", name="ck_coupon_minimum"),
    )
