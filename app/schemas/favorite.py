from pydantic import BaseModel

from app.schemas.product import ProductResponse


class FavoriteCreate(BaseModel):
    product_id: int


class FavoriteResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse

    model_config = {
        "from_attributes": True
    }
