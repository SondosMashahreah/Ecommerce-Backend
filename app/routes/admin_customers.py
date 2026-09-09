from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.admin import (
    get_current_admin,
)

from app.db.database import get_db

from app.models.user import User

from app.schemas.admin_customer import (
    AdminCustomerResponse,
    AdminCustomerRoleUpdate,
    AdminCustomerStatusUpdate,
)

from app.services.admin_customer import (
    get_admin_customer,
    get_admin_customers,
    update_customer_role,
    update_customer_status,
)


router = APIRouter(
    prefix="/admin/customers",
    tags=["Admin Customers"],
)


@router.get(
    "/",
    response_model=
        list[AdminCustomerResponse],
)
def list_customers(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_customers(
        db=db,
        search=search,
    )


@router.get(
    "/{user_id}",
    response_model=
        AdminCustomerResponse,
)
def customer_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    user = get_admin_customer(
        db=db,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}/status",
    response_model=
        AdminCustomerResponse,
)
def change_customer_status(
    user_id: int,
    data: AdminCustomerStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    if current_admin.id == user_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "You cannot disable "
                "your own admin account"
            ),
        )

    user = get_admin_customer(
        db=db,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return update_customer_status(
        db=db,
        user=user,
        is_active=data.is_active,
    )


@router.patch(
    "/{user_id}/role",
    response_model=
        AdminCustomerResponse,
)
def change_customer_role(
    user_id: int,
    data: AdminCustomerRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    if current_admin.id == user_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "You cannot change "
                "your own admin role"
            ),
        )

    user = get_admin_customer(
        db=db,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return update_customer_role(
        db=db,
        user=user,
        role=data.role,
    )