from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductItemCreate,
    ProductItemResponse,
    ProductResponse,
)
from app.services.minio_service import upload_file
from app.services.product import (
    create_product,
    create_product_item,
    get_products,
    search_products,
    get_product_by_id,
    get_categories,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", response_model=ProductResponse)
def add_product(
    name: str = Form(...),
    description: str | None = Form(None),
    price: float = Form(...),
    category: str = Form(...),

    # Initial item / variant.
    sku: str = Form(...),
    size: str | None = Form(None),
    color: str | None = Form(None),
    stock: int = Form(0),
    stock_limit: int = Form(5),

    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    video: UploadFile | None = File(None),

    db: Session = Depends(get_db),
):
    image_path = (
        upload_file(image, "products/images")
        if image
        else None
    )

    audio_path = (
        upload_file(audio, "products/audio")
        if audio
        else None
    )

    video_path = (
        upload_file(video, "products/videos")
        if video
        else None
    )

    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        item=ProductItemCreate(
            sku=sku,
            size=size,
            color=color,
            stock=stock,
            stock_limit=stock_limit,
        ),
    )

    try:
        return create_product(
            db=db,
            product_data=product_data,
            image_path=image_path,
            audio_path=audio_path,
            video_path=video_path,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@router.post(
    "/{product_id}/items",
    response_model=ProductItemResponse,
)
def add_product_item(
    product_id: int,
    data: ProductItemCreate,
    db: Session = Depends(get_db),
):
    try:
        item = create_product_item(
            db=db,
            product_id=product_id,
            item_data=data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return item


@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return get_products(db)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return get_categories(db)


@router.get(
    "/search",
    response_model=List[ProductResponse],
)
def fuzzy_search_products(
    q: str,
    db: Session = Depends(get_db),
):
    return search_products(db, q)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product
