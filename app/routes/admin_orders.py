from fastapi import (
    APIRouter,
    Depends,
)

from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.orm import Session

from app.core.admin import (
    get_current_admin,
)

from app.db.database import get_db

from app.models.order import OrderStatus
from app.models.user import User

from app.schemas.admin_order import (
    AdminOrderResponse,
    AdminOrderStatusUpdate,
)

from app.services.admin_order import (
    cancel_admin_order,
    get_admin_order,
    get_all_admin_orders,
)

from app.services.order import (
    generate_invoice_pdf,
    update_order_status,
)


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"],
)


@router.get(
    "/",
    response_model=
        list[AdminOrderResponse],
)
def list_orders(
    status: OrderStatus | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_all_admin_orders(
        db=db,
        status=status,
        search=search,
    )


@router.get(
    "/{order_id}",
    response_model=
        AdminOrderResponse,
)
def order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_order(
        db=db,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/status",
    response_model=
        AdminOrderResponse,
)
def change_status(
    order_id: int,
    data: AdminOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    update_order_status(
    db=db,
    order_id=order_id,
    new_status=data.status,
    allow_admin_override=True,
    )

    return get_admin_order(
        db=db,
        order_id=order_id,
    )


@router.patch(
    "/{order_id}/cancel",
    response_model=
        AdminOrderResponse,
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return cancel_admin_order(
        db=db,
        order_id=order_id,
    )


@router.get(
    "/{order_id}/invoice"
)
def invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    order = get_admin_order(
        db=db,
        order_id=order_id,
    )

    pdf_buffer = generate_invoice_pdf(
        db=db,
        user_id=order["user_id"],
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