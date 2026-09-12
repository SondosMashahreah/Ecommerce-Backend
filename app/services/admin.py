from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.product import Product, ProductItem
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
)


def get_admin_dashboard(db: Session): 



    completed_statuses = [
        OrderStatus.DONE,
        OrderStatus.RETURN_REQUESTED,
        OrderStatus.RETURNED,
        OrderStatus.REFUND_REQUESTED,
        OrderStatus.REFUNDED,
    ]

    revenue = (
        db.query(
            func.coalesce(
                func.sum(Order.total_amount),
                0
            )
        )
        .filter(
            Order.status.in_(completed_statuses)
        )
        .scalar()
    )

    orders_count = (
        db.query(Order)
        .count()
    )

    customers_count = (
        db.query(User)
        .filter(
            User.role == "customer"
        )
        .count()
    )

    products_count = (
        db.query(Product)
        .count()
    )

    product_items = (
        db.query(ProductItem)
        .all()
    )

    low_stock_count = sum(
        1
        for item in product_items
        if (
            item.available_stock
            <= item.stock_limit
        )
    )

    pending_orders = (
        db.query(Order)
        .filter(
            Order.status
            == OrderStatus.PENDING
        )
        .count()
    )

    refunds_count = (
        db.query(Order)
        .filter(
            Order.status.in_([
                OrderStatus.REFUND_REQUESTED,
                OrderStatus.REFUNDED,
            ])
        )
        .count()
    )

    if orders_count > 0:
        average_order_value = (
            float(revenue)
            / orders_count
        )
    else:
        average_order_value = 0




    revenue_rows = (
        db.query(
            func.date(Order.created_at).label(
                "order_date"
            ),
            func.sum(
                Order.total_amount
            ).label("total"),
        )
        .filter(
            Order.status.in_(completed_statuses)
        )
        .group_by(
            func.date(Order.created_at)
        )
        .order_by(
            func.date(Order.created_at)
        )
        .all()
    )

    revenue_over_time = [
        {
            "label": str(row.order_date),
            "value": float(row.total or 0),
        }
        for row in revenue_rows
    ]




    orders_rows = (
        db.query(
            func.date(Order.created_at).label(
                "order_date"
            ),
            func.count(Order.id).label(
                "count"
            ),
        )
        .group_by(
            func.date(Order.created_at)
        )
        .order_by(
            func.date(Order.created_at)
        )
        .all()
    )

    orders_over_time = [
        {
            "label": str(row.order_date),
            "value": float(row.count),
        }
        for row in orders_rows
    ]




    category_rows = (
        db.query(
            Product.category,
            func.sum(
                OrderItem.subtotal
            ).label("sales"),
        )
        .join(
            ProductItem,
            ProductItem.id
            == OrderItem.product_item_id,
        )
        .join(
            Product,
            Product.id
            == ProductItem.product_id,
        )
        .join(
            Order,
            Order.id
            == OrderItem.order_id,
        )
        .filter(
            Order.status.in_(completed_statuses)
        )
        .group_by(
            Product.category
        )
        .order_by(
            func.sum(
                OrderItem.subtotal
            ).desc()
        )
        .all()
    )

    sales_by_category = [
        {
            "category": row.category,
            "value": float(row.sales or 0),
        }
        for row in category_rows
    ]




    top_product_rows = (
        db.query(
            OrderItem.product_name,
            func.sum(
                OrderItem.quantity
            ).label("quantity"),
        )
        .join(
            Order,
            Order.id
            == OrderItem.order_id,
        )
        .filter(
            Order.status.in_(completed_statuses)
        )
        .group_by(
            OrderItem.product_name
        )
        .order_by(
            func.sum(
                OrderItem.quantity
            ).desc()
        )
        .limit(5)
        .all()
    )

    top_products = [
        {
            "product": row.product_name,
            "quantity": int(
                row.quantity or 0
            ),
        }
        for row in top_product_rows
    ]




    customer_rows = (
        db.query(
            func.date(
                User.created_at
            ).label("join_date"),
            func.count(
                User.id
            ).label("count"),
        )
        .filter(
            User.role == "customer"
        )
        .group_by(
            func.date(User.created_at)
        )
        .order_by(
            func.date(User.created_at)
        )
        .all()
    )

    new_customers = [
        {
            "label": str(row.join_date),
            "value": float(row.count),
        }
        for row in customer_rows
    ]


    return {
        "stats": {
            "revenue":
                float(revenue or 0),

            "orders":
                orders_count,

            "customers":
                customers_count,

            "products":
                products_count,

            "low_stock_products":
                low_stock_count,

            "pending_orders":
                pending_orders,

            "refunds":
                refunds_count,

            "average_order_value":
                float(
                    average_order_value
                ),
        },

        "revenue_over_time":
            revenue_over_time,

        "orders_over_time":
            orders_over_time,

        "sales_by_category":
            sales_by_category,

        "top_products":
            top_products,

        "new_customers":
            new_customers,
    }
