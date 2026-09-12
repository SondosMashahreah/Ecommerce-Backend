from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    product_id: int

    rating: int = Field(
        ge=1,
        le=5
    )


class RatingResponse(BaseModel):
    id: int
    product_id: int
    rating: int

    model_config = {
        "from_attributes": True
    }


class ProductRatingSummary(BaseModel):
    average_rating: float
    ratings_count: int
