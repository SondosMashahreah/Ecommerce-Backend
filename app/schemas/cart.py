from pydantic import BaseModel, Field

from app.schemas.product import ProductItemResponse, ProductResponse


class CartItemCreate(BaseModel):
    # New field used by variant-aware frontend.
    product_item_id: int | None = None

    # Temporary compatibility with the current frontend.
    product_id: int | None = None

    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_item_id: int
    product_id: int
    quantity: int
    product_item: ProductItemResponse
    product: ProductResponse

    model_config = {"from_attributes": True}
