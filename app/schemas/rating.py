from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    product_id: int

    rating: int = Field(
        ge=1,
        le=5
    )
    comment: str | None = Field(default=None, max_length=1000)


class RatingResponse(BaseModel):
    id: int
    product_id: int
    rating: int
    comment: str | None

    model_config = {
        "from_attributes": True
    }


class ProductReview(BaseModel):
    id: int
    rating: int
    comment: str
    user_name: str


class ProductRatingSummary(BaseModel):
    average_rating: float
    ratings_count: int
    reviews: list[ProductReview] = Field(default_factory=list)
