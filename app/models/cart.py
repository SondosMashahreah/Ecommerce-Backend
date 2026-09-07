from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    product_item_id = Column(
        Integer,
        ForeignKey("product_items.id"),
        nullable=False,
        index=True,
    )

    quantity = Column(Integer, nullable=False, default=1)

    product_item = relationship(
        "ProductItem",
        back_populates="cart_items",
    )

    @property
    def product_id(self) -> int:
        return self.product_item.product_id

    @property
    def product(self):
        # Compatibility for the current frontend.
        return self.product_item.product
