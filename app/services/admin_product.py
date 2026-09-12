from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, ProductItem


def get_admin_products(db: Session):
    return (
        db.query(Product)
        .options(selectinload(Product.items))
        .order_by(Product.id.desc())
        .all()
    )


def get_admin_product(
    db: Session,
    product_id: int,
):
    product = (
        db.query(Product)
        .options(selectinload(Product.items))
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


def update_admin_product(
    db: Session,
    product_id: int,
    name: str | None = None,
    description: str | None = None,
    price: float | None = None,
    category: str | None = None,
    image_path: str | None = None,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if name is not None:
        product.name = name

    if description is not None:
        product.description = description

    if price is not None:
        if price <= 0:
            raise HTTPException(
                status_code=400,
                detail="Price must be greater than 0",
            )
        product.price = price

    if category is not None:
        product.category = category

    if image_path is not None:
        product.image_path = image_path

    db.commit()
    db.refresh(product)

    return product


def delete_admin_product(
    db: Session,
    product_id: int,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }


def create_product_item(
    db: Session,
    product_id: int,
    sku: str,
    size: str | None,
    color: str | None,
    stock: int,
    stock_limit: int,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    existing_sku = (
        db.query(ProductItem)
        .filter(ProductItem.sku == sku)
        .first()
    )

    if existing_sku:
        raise HTTPException(
            status_code=409,
            detail="SKU already exists",
        )

    item = ProductItem(
        product_id=product_id,
        sku=sku,
        size=size,
        color=color,
        stock=stock,
        stock_limit=stock_limit,
        reserved_stock=0,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def update_product_item(
    db: Session,
    item_id: int,
    sku: str | None = None,
    size: str | None = None,
    color: str | None = None,
    stock: int | None = None,
    stock_limit: int | None = None,
):
    item = (
        db.query(ProductItem)
        .filter(ProductItem.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product item not found",
        )

    if sku is not None:
        existing_sku = (
            db.query(ProductItem)
            .filter(
                ProductItem.sku == sku,
                ProductItem.id != item_id,
            )
            .first()
        )

        if existing_sku:
            raise HTTPException(
                status_code=409,
                detail="SKU already exists",
            )

        item.sku = sku

    if size is not None:
        item.size = size

    if color is not None:
        item.color = color

    if stock is not None:
        if stock < item.reserved_stock:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Stock cannot be less than reserved stock"
                ),
            )

        item.stock = stock

    if stock_limit is not None:
        if stock_limit < 0:
            raise HTTPException(
                status_code=400,
                detail="Stock limit cannot be negative",
            )

        item.stock_limit = stock_limit

    db.commit()
    db.refresh(item)

    return item


def delete_product_item(
    db: Session,
    item_id: int,
):
    item = (
        db.query(ProductItem)
        .filter(ProductItem.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product item not found",
        )

    if item.reserved_stock > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete item with reserved stock"
            ),
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Product item deleted successfully"
    }
