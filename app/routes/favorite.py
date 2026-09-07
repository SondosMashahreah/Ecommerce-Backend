from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user

from app.schemas.favorite import (
    FavoriteCreate,
    FavoriteResponse
)

from app.services.favorite import (
    add_to_favorites,
    get_favorites,
    remove_from_favorites
)


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


@router.post("/", response_model=FavoriteResponse)
def create_favorite(
    data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return add_to_favorites(
        db=db,
        user_id=current_user.id,
        product_id=data.product_id
    )


@router.get("/", response_model=List[FavoriteResponse])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_favorites(
        db=db,
        user_id=current_user.id
    )


@router.delete("/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favorite = remove_from_favorites(
        db=db,
        user_id=current_user.id,
        favorite_id=favorite_id
    )

    if not favorite:
        raise HTTPException(
            status_code=404,
            detail="Favorite not found"
        )

    return {
        "message": "Favorite removed successfully"
    }