from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.admin import get_current_admin
from app.models.user import User
from app.schemas.admin import (
    AdminDashboardResponse,
)
from app.services.admin import (
    get_admin_dashboard,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def admin_dashboard(
    db: Session = Depends(get_db),

    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_dashboard(db)
