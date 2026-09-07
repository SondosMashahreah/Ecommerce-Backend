from pydantic import BaseModel, Field


class ProductItemCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    size: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=100)
    stock: int = Field(default=0, ge=0)
    stock_limit: int = Field(default=5, ge=0)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    item: ProductItemCreate


class ProductItemResponse(BaseModel):
    id: int
    product_id: int
    sku: str
    size: str | None
    color: str | None
    stock: int
    stock_limit: int
    reserved_stock: int
    available_stock: int
    stock_status: str

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    category: str
    image_path: str | None
    audio_path: str | None
    video_path: str | None

    # Computed compatibility field; not stored in products.
    stock: int

    items: list[ProductItemResponse] = []

    model_config = {"from_attributes": True}
