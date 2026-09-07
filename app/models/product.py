from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)

    image_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)

    items = relationship(
        "ProductItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def stock(self) -> int:
        # Compatibility for the current frontend.
        # Stock is no longer a products-table column.
        return sum(item.available_stock for item in self.items)


class ProductItem(Base):
    __tablename__ = "product_items"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sku = Column(String(100), unique=True, nullable=False, index=True)
    size = Column(String(100), nullable=True)
    color = Column(String(100), nullable=True)

    # Physical stock.
    stock = Column(Integer, nullable=False, default=0)

    # Low-stock alert threshold.
    stock_limit = Column(Integer, nullable=False, default=5)

    # Stock reserved by carts / checkout.
    reserved_stock = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    product = relationship("Product", back_populates="items")
    cart_items = relationship("CartItem", back_populates="product_item")

    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_product_items_stock_non_negative"),
        CheckConstraint("stock_limit >= 0", name="ck_product_items_stock_limit_non_negative"),
        CheckConstraint("reserved_stock >= 0", name="ck_product_items_reserved_non_negative"),
        CheckConstraint("reserved_stock <= stock", name="ck_product_items_reserved_not_above_stock"),
    )

    @property
    def available_stock(self) -> int:
        return max(self.stock - self.reserved_stock, 0)

    @property
    def stock_status(self) -> str:
        if self.available_stock == 0:
            return "out_of_stock"
        if self.available_stock <= self.stock_limit:
            return "low_stock"
        return "in_stock"
