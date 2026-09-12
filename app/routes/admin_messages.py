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

from app.schemas.admin_message import (
    AdminMessageResponse,
)

from app.services.admin_message import (
    delete_message,
    get_admin_message,
    get_admin_messages,
    mark_message_read,
)


router = APIRouter(
    prefix="/admin/messages",
    tags=["Admin Messages"],
)


@router.get(
    "/",
    response_model=
        list[AdminMessageResponse],
)
def list_messages(
    search: str | None = None,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_messages(
        db=db,
        search=search,
        unread_only=unread_only,
    )


@router.get(
    "/{message_id}",
    response_model=
        AdminMessageResponse,
)
def message_details(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    message = get_admin_message(
        db=db,
        message_id=message_id,
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found",
        )

    return message


@router.patch(
    "/{message_id}/read",
    response_model=
        AdminMessageResponse,
)
def read_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    message = get_admin_message(
        db=db,
        message_id=message_id,
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found",
        )

    return mark_message_read(
        db=db,
        message=message,
    )


@router.delete("/{message_id}")
def remove_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    message = get_admin_message(
        db=db,
        message_id=message_id,
    )

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found",
        )

    delete_message(
        db=db,
        message=message,
    )

    return {
        "message":
            "Message deleted successfully"
    }
