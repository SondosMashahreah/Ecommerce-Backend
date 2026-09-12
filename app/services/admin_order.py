from datetime import datetime

from fastapi import HTTPException

from sqlalchemy import or_
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.models.order import (
    Order,
    OrderStatus,
    OrderStatusHistory,
)

from app.models.product import (
    ProductItem,
)

from app.models.user import User


def build_admin_order(
    order: Order,
    user: User,
):
    return {
        "id": order.id,
        "user_id": order.user_id,

        "customer": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },

        "status": order.status,
        "total_amount":
            order.total_amount,

        "created_at":
            order.created_at,

        "updated_at":
            order.updated_at,

        "cancelled_at":
            order.cancelled_at,

        "completed_at":
            order.completed_at,

        "items":
            order.items,

        "status_history":
            order.status_history,
    }


def get_all_admin_orders(
    db: Session,
    status: OrderStatus | None = None,
    search: str | None = None,
):
    query = (
        db.query(Order, User)
        .join(
            User,
            User.id == Order.user_id,
        )
        .options(
            joinedload(Order.items),
            joinedload(
                Order.status_history
            ),
        )
    )

    if status:
        query = query.filter(
            Order.status == status
        )

    if search:
        search = search.strip()
        pattern = f"%{search}%"

        conditions = [
            User.name.ilike(pattern),
            User.email.ilike(pattern),
        ]

        if search.isdigit():
            conditions.append(
                Order.id == int(search)
            )

        query = query.filter(
            or_(*conditions)
        )

    rows = (
        query
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    return [
        build_admin_order(
            order,
            user,
        )
        for order, user in rows
    ]


def get_admin_order(
    db: Session,
    order_id: int,
):
    row = (
        db.query(Order, User)
        .join(
            User,
            User.id == Order.user_id,
        )
        .options(
            joinedload(Order.items),
            joinedload(
                Order.status_history
            ),
        )
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    order, user = row

    return build_admin_order(
        order,
        user,
    )


def cancel_admin_order(
    db: Session,
    order_id: int,
):
    try:
        order = (
            db.query(Order)
            .options(
                joinedload(Order.items)
            )
            .filter(
                Order.id == order_id
            )
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        blocked = {
            OrderStatus.CANCELLED,
            OrderStatus.DONE,
            OrderStatus.RETURNED,
            OrderStatus.REFUNDED,
            OrderStatus.RETURN_REQUESTED,
            OrderStatus.REFUND_REQUESTED,
        }

        if order.status in blocked:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This order cannot "
                    "be cancelled"
                ),
            )

        for item in order.items:
            product_item = (
                db.query(ProductItem)
                .filter(
                    ProductItem.id
                    == item.product_item_id
                )
                .with_for_update()
                .first()
            )

            if product_item:
                product_item.stock += (
                    item.quantity
                )

        order.status = (
            OrderStatus.CANCELLED
        )

        order.cancelled_at = (
            datetime.utcnow()
        )

        history = OrderStatusHistory(
            order_id=order.id,
            status=
                OrderStatus.CANCELLED,
        )

        db.add(history)
        db.commit()

        return get_admin_order(
            db=db,
            order_id=order.id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise
