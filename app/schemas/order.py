from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    coupon_code: str | None = None


class OrderItemResponse(BaseModel):
    id: int
    product_item_id: int

    product_name: str
    sku: str

    unit_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}


class OrderStatusHistoryResponse(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float

    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    completed_at: datetime | None

    items: list[OrderItemResponse] = []
    status_history: list[OrderStatusHistoryResponse] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
