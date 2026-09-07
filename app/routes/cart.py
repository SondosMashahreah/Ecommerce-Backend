from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.cart import CartItemCreate, CartItemResponse
from app.services.cart import (
    add_to_cart,
    clear_cart,
    decrement_cart_item,
    get_cart,
    increment_cart_item,
    remove_from_cart,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.post("/", response_model=CartItemResponse)
def create_cart_item(
    data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if (
        data.product_item_id is None
        and data.product_id is None
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "product_item_id is required. "
                "product_id is accepted temporarily "
                "for backward compatibility."
            ),
        )

    return add_to_cart(
        db=db,
        user_id=current_user.id,
        product_item_id=data.product_item_id,
        product_id=data.product_id,
        quantity=data.quantity,
    )


@router.get("/", response_model=List[CartItemResponse])
def list_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_cart(
        db=db,
        user_id=current_user.id,
    )


@router.put(
    "/{cart_item_id}/increment",
    response_model=CartItemResponse,
)
def increment_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return increment_cart_item(
        db=db,
        user_id=current_user.id,
        cart_item_id=cart_item_id,
    )


@router.put("/{cart_item_id}/decrement")
def decrement_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = decrement_cart_item(
        db=db,
        user_id=current_user.id,
        cart_item_id=cart_item_id,
    )

    if item is None:
        return {"message": "Item removed from cart"}

    return {
        "message": "Quantity decreased",
        "item": item,
    }


@router.delete("/{cart_item_id}")
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = remove_from_cart(
        db=db,
        user_id=current_user.id,
        cart_item_id=cart_item_id,
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    return {"message": "Item removed from cart"}


@router.delete("/")
def delete_all_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clear_cart(
        db=db,
        user_id=current_user.id,
    )

    return {"message": "Cart cleared"}
