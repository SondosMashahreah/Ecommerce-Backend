from pydantic import BaseModel, Field


class AdminProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    price: float | None = Field(
        default=None,
        gt=0,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class ProductItemCreateAdmin(BaseModel):
    sku: str = Field(
        min_length=1,
        max_length=100,
    )

    size: str | None = Field(
        default=None,
        max_length=100,
    )

    color: str | None = Field(
        default=None,
        max_length=100,
    )

    stock: int = Field(
        default=0,
        ge=0,
    )

    stock_limit: int = Field(
        default=5,
        ge=0,
    )


class ProductItemUpdateAdmin(BaseModel):
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    size: str | None = Field(
        default=None,
        max_length=100,
    )

    color: str | None = Field(
        default=None,
        max_length=100,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )

    stock_limit: int | None = Field(
        default=None,
        ge=0,
    )