from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.cart import CartItem
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
)
from app.models.product import Product, ProductItem

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.models.user import User


def create_order(db: Session, user_id: int):
    try:

        cart_items = (
            db.query(CartItem)
            .options(
                joinedload(CartItem.product_item)
                .joinedload(ProductItem.product)
            )
            .filter(CartItem.user_id == user_id)
            .all()
        )

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty",
            )

        # 2. Create the order.
        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=0,
        )

        db.add(order)
        db.flush()

        total_amount = 0.0

        for cart_item in cart_items:
            product_item = (
                db.query(ProductItem)
                .filter(
                    ProductItem.id
                    == cart_item.product_item_id
                )
                .with_for_update()
                .first()
            )

            if not product_item:
                raise HTTPException(
                    status_code=404,
                    detail="Product item not found",
                )

            product = (
                db.query(Product)
                .filter(
                    Product.id
                    == product_item.product_id
                )
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found",
                )

            quantity = cart_item.quantity

            # The cart should already have reserved this quantity.
            if product_item.reserved_stock < quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Reserved stock is invalid for "
                        f"{product.name}"
                    ),
                )

            if product_item.stock < quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Not enough physical stock for "
                        f"{product.name}"
                    ),
                )

            unit_price = product.price
            subtotal = unit_price * quantity

            order_item = OrderItem(
                order_id=order.id,
                product_item_id=product_item.id,
                product_name=product.name,
                sku=product_item.sku,
                unit_price=unit_price,
                quantity=quantity,
                subtotal=subtotal,
            )

            db.add(order_item)

            total_amount += subtotal


            product_item.stock -= quantity
            product_item.reserved_stock -= quantity

            db.delete(cart_item)

        order.total_amount = total_amount

        # 6. First status-history entry.
        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.PENDING,
        )

        db.add(history)

        db.commit()

        return get_order_by_id(
            db=db,
            user_id=user_id,
            order_id=order.id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


def get_orders(db: Session, user_id: int):
    return (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(
    db: Session,
    user_id: int,
    order_id: int,
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order

def cancel_order(
    db: Session,
    user_id: int,
    order_id: int,
):
    try:
        order = (
            db.query(Order)
            .options(joinedload(Order.items))
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        # Already cancelled
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=400,
                detail="Order is already cancelled",
            )

        # Completed orders cannot be cancelled.
        if order.status == OrderStatus.DONE:
            raise HTTPException(
                status_code=400,
                detail="Completed order cannot be cancelled",
            )

        # Return purchased quantities to inventory.
        for order_item in order.items:
            product_item = (
                db.query(ProductItem)
                .filter(
                    ProductItem.id
                    == order_item.product_item_id
                )
                .with_for_update()
                .first()
            )

            if not product_item:
                raise HTTPException(
                    status_code=404,
                    detail="Product item not found",
                )

            product_item.stock += order_item.quantity

        # Change order status.
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()

        # Save status in history.
        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.CANCELLED,
        )

        db.add(history)

        db.commit()

        return get_order_by_id(
            db=db,
            user_id=user_id,
            order_id=order.id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

def update_order_status(
    db: Session,
    order_id: int,
    new_status: OrderStatus,
    allow_admin_override: bool = False,
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

        if order.status == new_status:
            return order

        allowed_transitions = {
            OrderStatus.PENDING: [
                OrderStatus.CONFIRMED,
            ],

            OrderStatus.CONFIRMED: [
                OrderStatus.PROCESSING,
            ],

            OrderStatus.PROCESSING: [
                OrderStatus.READY,
            ],

            OrderStatus.READY: [
                OrderStatus.DONE,
            ],

            OrderStatus.RETURN_REQUESTED: [
                OrderStatus.RETURNED,
            ],

            OrderStatus.REFUND_REQUESTED: [
                OrderStatus.REFUNDED,
            ],
        }

        main_order_statuses = {
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.READY,
            OrderStatus.DONE,
        }

        if allow_admin_override:
            if (
                order.status
                not in main_order_statuses
                or new_status
                not in main_order_statuses
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Admin override is only allowed "
                        "between normal order statuses"
                    ),
                )

        else:
            allowed_next_statuses = (
                allowed_transitions.get(
                    order.status,
                    [],
                )
            )

            if (
                new_status
                not in allowed_next_statuses
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot change order status "
                        f"from {order.status.value} "
                        f"to {new_status.value}"
                    ),
                )

        if (
            new_status
            == OrderStatus.RETURNED
        ):
            for order_item in order.items:
                product_item = (
                    db.query(ProductItem)
                    .filter(
                        ProductItem.id
                        == order_item.product_item_id
                    )
                    .with_for_update()
                    .first()
                )

                if product_item:
                    product_item.stock += (
                        order_item.quantity
                    )

        order.status = new_status

        if (
            new_status
            == OrderStatus.DONE
        ):
            order.completed_at = (
                datetime.utcnow()
            )

        elif (
            allow_admin_override
            and new_status
            != OrderStatus.DONE
        ):
            order.completed_at = None

        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
        )

        db.add(history)
        db.commit()

        return (
            db.query(Order)
            .options(
                joinedload(Order.items),
                joinedload(
                    Order.status_history
                ),
            )
            .filter(
                Order.id == order.id
            )
            .first()
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

        if (
            new_status
            == OrderStatus.RETURNED
        ):
            for order_item in order.items:
                product_item = (
                    db.query(ProductItem)
                    .filter(
                        ProductItem.id
                        == order_item.product_item_id
                    )
                    .with_for_update()
                    .first()
                )

                if product_item:
                    product_item.stock += (
                        order_item.quantity
                    )

        order.status = new_status

        if new_status == OrderStatus.DONE:
            order.completed_at = (
                datetime.utcnow()
            )

        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
        )

        db.add(history)
        db.commit()

        return (
            db.query(Order)
            .options(
                joinedload(Order.items),
                joinedload(
                    Order.status_history
                ),
            )
            .filter(
                Order.id == order.id
            )
            .first()
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

def request_order_return(
    db: Session,
    user_id: int,
    order_id: int,
):
    try:
        order = (
            db.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        if order.status != OrderStatus.DONE:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Return can only be requested "
                    "for completed orders"
                ),
            )

        order.status = (
            OrderStatus.RETURN_REQUESTED
        )

        history = OrderStatusHistory(
            order_id=order.id,
            status=(
                OrderStatus.RETURN_REQUESTED
            ),
        )

        db.add(history)
        db.commit()

        return get_order_by_id(
            db=db,
            user_id=user_id,
            order_id=order_id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

def request_order_refund(
    db: Session,
    user_id: int,
    order_id: int,
):
    try:
        order = (
            db.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        if order.status != OrderStatus.DONE:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Refund can only be requested "
                    "for completed orders"
                ),
            )

        order.status = (
            OrderStatus.REFUND_REQUESTED
        )

        history = OrderStatusHistory(
            order_id=order.id,
            status=(
                OrderStatus.REFUND_REQUESTED
            ),
        )

        db.add(history)
        db.commit()

        return get_order_by_id(
            db=db,
            user_id=user_id,
            order_id=order_id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

def reorder_previous_order(
    db: Session,
    user_id: int,
    order_id: int,
):
    try:
        order = (
            db.query(Order)
            .options(joinedload(Order.items))
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        added_items = []
        skipped_items = []

        for order_item in order.items:

            product_item = (
                db.query(ProductItem)
                .filter(
                    ProductItem.id
                    == order_item.product_item_id
                )
                .with_for_update()
                .first()
            )

            if not product_item:
                skipped_items.append({
                    "product_name":
                        order_item.product_name,

                    "reason":
                        "Product item no longer exists",
                })

                continue

            available_stock = (
                product_item.stock
                - product_item.reserved_stock
            )

            if available_stock <= 0:
                skipped_items.append({
                    "product_name":
                        order_item.product_name,

                    "reason":
                        "Out of stock",
                })

                continue

            quantity_to_add = min(
                order_item.quantity,
                available_stock,
            )

            cart_item = (
                db.query(CartItem)
                .filter(
                    CartItem.user_id == user_id,

                    CartItem.product_item_id
                    == product_item.id,
                )
                .first()
            )

            if cart_item:
                cart_item.quantity += (
                    quantity_to_add
                )

            else:
                cart_item = CartItem(
                    user_id=user_id,

                    product_item_id=
                        product_item.id,

                    quantity=
                        quantity_to_add,
                )

                db.add(cart_item)

            product_item.reserved_stock += (
                quantity_to_add
            )

            added_items.append({
                "product_name":
                    order_item.product_name,

                "quantity":
                    quantity_to_add,
            })

        if not added_items:
            raise HTTPException(
                status_code=409,
                detail=(
                    "None of the items are "
                    "currently available"
                ),
            )

        db.commit()

        return {
            "message":
                "Previous order added to cart",

            "added_items":
                added_items,

            "skipped_items":
                skipped_items,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

def generate_invoice_pdf(
    db: Session,
    user_id: int,
    order_id: int,
):
    order = get_order_by_id(
        db=db,
        user_id=user_id,
        order_id=order_id,
    )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    y = height - 60

    pdf.setFont(
        "Helvetica-Bold",
        20,
    )

    pdf.drawString(
        50,
        y,
        "Ecommerce Invoice",
    )

    y -= 40

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        50,
        y,
        f"Order ID: #{order.id}",
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Customer: {user.name}",
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Email: {user.email}",
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Status: {order.status.value}",
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        (
            f"Date: "
            f"{order.created_at.strftime('%Y-%m-%d %H:%M')}"
        ),
    )

    y -= 40

    pdf.setFont(
        "Helvetica-Bold",
        11,
    )

    pdf.drawString(
        50,
        y,
        "Product",
    )

    pdf.drawString(
        300,
        y,
        "Qty",
    )

    pdf.drawString(
        350,
        y,
        "Price",
    )

    pdf.drawString(
        450,
        y,
        "Subtotal",
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        10,
    )

    for item in order.items:

        if y < 80:
            pdf.showPage()

            y = height - 60

        pdf.drawString(
            50,
            y,
            item.product_name[:35],
        )

        pdf.drawString(
            300,
            y,
            str(item.quantity),
        )

        pdf.drawString(
            350,
            y,
            f"${item.unit_price:.2f}",
        )

        pdf.drawString(
            450,
            y,
            f"${item.subtotal:.2f}",
        )

        y -= 20

    y -= 20

    pdf.setFont(
        "Helvetica-Bold",
        13,
    )

    pdf.drawString(
        350,
        y,
        (
            f"Total: "
            f"${order.total_amount:.2f}"
        ),
    )

    pdf.save()

    buffer.seek(0)

    return buffer