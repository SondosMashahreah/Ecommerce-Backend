from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.admin import get_current_admin
from app.models.user import User
from app.schemas.product import (
    ProductResponse,
    ProductItemResponse,
)
from app.schemas.admin_product import (
    AdminProductUpdate,
    ProductItemCreateAdmin,
    ProductItemUpdateAdmin,
)
from app.services.admin_product import (
    get_admin_products,
    get_admin_product,
    update_admin_product,
    delete_admin_product,
    create_product_item,
    update_product_item,
    delete_product_item,
)
from app.services.product import create_product
from app.schemas.product import ProductCreate
from app.services.supabase_storage_service import upload_file


router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"],
)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def list_admin_products(
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def admin_product_details(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return get_admin_product(
        db,
        product_id,
    )


@router.post(
    "/",
    response_model=ProductResponse,
)
def admin_create_product(
    name: str = Form(...),
    description: str | None = Form(None),
    price: float = Form(...),
    category: str = Form(...),

    sku: str = Form(...),
    size: str | None = Form(None),
    color: str | None = Form(None),
    stock: int = Form(0),
    stock_limit: int = Form(5),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    image_path = (
        upload_file(
            image,
            "products/images",
        )
        if image
        else None
    )

    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        item={
            "sku": sku,
            "size": size,
            "color": color,
            "stock": stock,
            "stock_limit": stock_limit,
        },
    )

    return create_product(
        db=db,
        product_data=product_data,
        image_path=image_path,
    )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def admin_edit_product(
    product_id: int,
    data: AdminProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return update_admin_product(
        db=db,
        product_id=product_id,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
    )


@router.post(
    "/{product_id}/image",
    response_model=ProductResponse,
)
def admin_replace_product_image(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    image_path = upload_file(
        image,
        "products/images",
    )

    return update_admin_product(
        db=db,
        product_id=product_id,
        image_path=image_path,
    )


@router.delete(
    "/{product_id}",
)
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return delete_admin_product(
        db,
        product_id,
    )


@router.post(
    "/{product_id}/items",
    response_model=ProductItemResponse,
)
def admin_add_product_item(
    product_id: int,
    data: ProductItemCreateAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return create_product_item(
        db=db,
        product_id=product_id,
        sku=data.sku,
        size=data.size,
        color=data.color,
        stock=data.stock,
        stock_limit=data.stock_limit,
    )


@router.patch(
    "/items/{item_id}",
    response_model=ProductItemResponse,
)
def admin_edit_product_item(
    item_id: int,
    data: ProductItemUpdateAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return update_product_item(
        db=db,
        item_id=item_id,
        sku=data.sku,
        size=data.size,
        color=data.color,
        stock=data.stock,
        stock_limit=data.stock_limit,
    )


@router.delete(
    "/items/{item_id}",
)
def admin_delete_product_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    return delete_product_item(
        db,
        item_id,
    )
