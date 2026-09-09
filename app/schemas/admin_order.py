from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.schemas.order import (
    OrderItemResponse,
    OrderStatusHistoryResponse,
)


class AdminOrderCustomer(BaseModel):
    id: int
    name: str
    email: str


class AdminOrderResponse(BaseModel):
    id: int
    user_id: int

    customer: AdminOrderCustomer

    status: OrderStatus
    total_amount: float

    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None
    completed_at: datetime | None

    items: list[OrderItemResponse]
    status_history: list[
        OrderStatusHistoryResponse
    ]


class AdminOrderStatusUpdate(BaseModel):
    status: OrderStatus