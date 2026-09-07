from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user

from app.schemas.order import (
    OrderResponse,
    OrderStatusUpdate,
)

from app.services.order import (
    cancel_order,
    create_order,
    generate_invoice_pdf,
    get_order_by_id,
    get_orders,
    reorder_previous_order,
    request_order_refund,
    request_order_return,
    update_order_status,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/", response_model=OrderResponse)
def create_new_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_order(
        db=db,
        user_id=current_user.id,
    )


@router.get("/", response_model=List[OrderResponse])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_orders(
        db=db,
        user_id=current_user.id,
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_order(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def change_order_status(
    order_id: int,
    data: OrderStatusUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return update_order_status(
        db=db,
        order_id=order_id,
        new_status=data.status,
    )

@router.post(
    "/{order_id}/return",
    response_model=OrderResponse,
)
def request_return(
    order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    return request_order_return(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

@router.post(
    "/{order_id}/refund",
    response_model=OrderResponse,
)
def request_refund(
    order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    return request_order_refund(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

@router.post(
    "/{order_id}/reorder"
)
def reorder_order(
    order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    return reorder_previous_order(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

@router.get(
    "/{order_id}/invoice"
)
def download_invoice(
    order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    pdf_buffer = generate_invoice_pdf(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
    )

    return StreamingResponse(
        pdf_buffer,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
                (
                    "attachment; "
                    f"filename=invoice-{order_id}.pdf"
                )
        },
    )

