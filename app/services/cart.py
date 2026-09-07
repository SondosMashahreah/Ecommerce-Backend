from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.cart import CartItem
from app.models.product import Product, ProductItem


def _get_item_for_cart(
    db: Session,
    product_item_id: int | None = None,
    product_id: int | None = None,
):
    if product_item_id is not None:
        return (
            db.query(ProductItem)
            .filter(ProductItem.id == product_item_id)
            .with_for_update()
            .first()
        )

    if product_id is not None:
        # Temporary compatibility with the current frontend.
        # Once variants are selectable, send product_item_id.
        return (
            db.query(ProductItem)
            .filter(ProductItem.product_id == product_id)
            .order_by(ProductItem.id.asc())
            .with_for_update()
            .first()
        )

    return None


def add_to_cart(
    db: Session,
    user_id: int,
    quantity: int = 1,
    product_item_id: int | None = None,
    product_id: int | None = None,
):
    if quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1",
        )

    item = _get_item_for_cart(
        db=db,
        product_item_id=product_item_id,
        product_id=product_id,
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product item not found",
        )

    if item.available_stock < quantity:
        raise HTTPException(
            status_code=409,
            detail="Not enough stock available",
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_item_id == item.id,
        )
        .first()
    )

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_item_id=item.id,
            quantity=quantity,
        )
        db.add(cart_item)

    # Cart reserves stock. Physical stock is not reduced here.
    item.reserved_stock += quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


def get_cart(db: Session, user_id: int):
    return (
        db.query(CartItem)
        .options(
            joinedload(CartItem.product_item)
            .joinedload(ProductItem.product)
            .joinedload(Product.items)
        )
        .filter(CartItem.user_id == user_id)
        .all()
    )


def increment_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    item = (
        db.query(ProductItem)
        .filter(ProductItem.id == cart_item.product_item_id)
        .with_for_update()
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product item not found",
        )

    if item.available_stock <= 0:
        raise HTTPException(
            status_code=409,
            detail="Product item is out of stock",
        )

    cart_item.quantity += 1
    item.reserved_stock += 1

    db.commit()
    db.refresh(cart_item)

    return cart_item


def decrement_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    item = (
        db.query(ProductItem)
        .filter(ProductItem.id == cart_item.product_item_id)
        .with_for_update()
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product item not found",
        )

    item.reserved_stock = max(
        item.reserved_stock - 1,
        0,
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.commit()
        db.refresh(cart_item)
        return cart_item

    db.delete(cart_item)
    db.commit()
    return None


def remove_from_cart(
    db: Session,
    user_id: int,
    cart_item_id: int,
):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if not cart_item:
        return None

    item = (
        db.query(ProductItem)
        .filter(ProductItem.id == cart_item.product_item_id)
        .with_for_update()
        .first()
    )

    if item:
        item.reserved_stock = max(
            item.reserved_stock - cart_item.quantity,
            0,
        )

    db.delete(cart_item)
    db.commit()
    return cart_item


def clear_cart(db: Session, user_id: int):
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )

    for cart_item in cart_items:
        item = (
            db.query(ProductItem)
            .filter(ProductItem.id == cart_item.product_item_id)
            .with_for_update()
            .first()
        )

        if item:
            item.reserved_stock = max(
                item.reserved_stock - cart_item.quantity,
                0,
            )

        db.delete(cart_item)

    db.commit()
