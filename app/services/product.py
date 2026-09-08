from sqlalchemy.orm import Session

from app.models.product import Product, ProductItem
from app.schemas.product import ProductCreate, ProductItemCreate


def create_product(
    db: Session,
    product_data: ProductCreate,
    image_path: str | None = None,
    audio_path: str | None = None,
    video_path: str | None = None,
):
    existing_item = (
        db.query(ProductItem)
        .filter(ProductItem.sku == product_data.item.sku)
        .first()
    )

    if existing_item:
        raise ValueError("SKU already exists")

    try:
        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category=product_data.category,
            image_path=image_path,
            audio_path=audio_path,
            video_path=video_path,
        )

        db.add(product)
        db.flush()

        item = ProductItem(
            product_id=product.id,
            sku=product_data.item.sku,
            size=product_data.item.size,
            color=product_data.item.color,
            stock=product_data.item.stock,
            stock_limit=product_data.item.stock_limit,
            reserved_stock=0,
        )

        db.add(item)

        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        raise


def create_product_item(
    db: Session,
    product_id: int,
    item_data: ProductItemCreate,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return None

    existing_item = (
        db.query(ProductItem)
        .filter(ProductItem.sku == item_data.sku)
        .first()
    )

    if existing_item:
        raise ValueError("SKU already exists")

    try:
        item = ProductItem(
            product_id=product_id,
            sku=item_data.sku,
            size=item_data.size,
            color=item_data.color,
            stock=item_data.stock,
            stock_limit=item_data.stock_limit,
            reserved_stock=0,
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    except Exception:
        db.rollback()
        raise


def get_products(db: Session):
    return (
        db.query(Product)
        .order_by(Product.id.desc())
        .all()
    )


def get_product_by_id(
    db: Session,
    product_id: int,
):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


def get_categories(db: Session):
    rows = (
        db.query(Product.category)
        .filter(Product.category.isnot(None))
        .distinct()
        .order_by(Product.category.asc())
        .all()
    )

    return [
        category
        for (category,) in rows
        if category
    ]


def search_products(
    db: Session,
    query: str,
):
    search_term = query.strip()

    if not search_term:
        return get_products(db)

    pattern = f"%{search_term}%"

    return (
        db.query(Product)
        .filter(
            Product.name.ilike(pattern)
            | Product.description.ilike(pattern)
            | Product.category.ilike(pattern)
        )
        .order_by(Product.id.desc())
        .all()
    )