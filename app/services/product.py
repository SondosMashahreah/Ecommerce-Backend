import uuid

from rapidfuzz import fuzz
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, ProductItem
from app.schemas.product import ProductCreate, ProductItemCreate


def _build_unique_sku(
    db: Session,
    requested_sku: str | None,
    product_name: str,
) -> str:
    if requested_sku:
        clean_sku = requested_sku.strip().upper()

        existing = (
            db.query(ProductItem)
            .filter(ProductItem.sku == clean_sku)
            .first()
        )

        if existing:
            raise ValueError("SKU already exists")

        return clean_sku

    prefix = "".join(
        char
        for char in product_name.upper()
        if char.isalnum()
    )[:8] or "ITEM"

    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def create_product(
    db: Session,
    product_data: ProductCreate,
    image_path: str | None = None,
    audio_path: str | None = None,
    video_path: str | None = None,
):
    new_product = Product(
        name=product_data.name.strip(),
        description=product_data.description,
        price=product_data.price,
        category=product_data.category.strip(),
        image_path=image_path,
        audio_path=audio_path,
        video_path=video_path,
    )

    db.add(new_product)
    db.flush()

    sku = _build_unique_sku(
        db=db,
        requested_sku=product_data.item.sku,
        product_name=product_data.name,
    )

    first_item = ProductItem(
        product_id=new_product.id,
        sku=sku,
        size=product_data.item.size.strip() if product_data.item.size else None,
        color=product_data.item.color.strip() if product_data.item.color else None,
        stock=product_data.item.stock,
        stock_limit=product_data.item.stock_limit,
        reserved_stock=0,
    )

    db.add(first_item)
    db.commit()

    return get_product_by_id(db, new_product.id)


def create_product_item(
    db: Session,
    product_id: int,
    item_data: ProductItemCreate,
):
    product = get_product_by_id(db, product_id)

    if not product:
        return None

    sku = _build_unique_sku(
        db=db,
        requested_sku=item_data.sku,
        product_name=product.name,
    )

    new_item = ProductItem(
        product_id=product_id,
        sku=sku,
        size=item_data.size.strip() if item_data.size else None,
        color=item_data.color.strip() if item_data.color else None,
        stock=item_data.stock,
        stock_limit=item_data.stock_limit,
        reserved_stock=0,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


def get_products(db: Session):
    return (
        db.query(Product)
        .options(selectinload(Product.items))
        .all()
    )


def get_categories(db: Session):
    categories = (
        db.query(Product.category)
        .filter(Product.category.isnot(None))
        .filter(Product.category != "")
        .distinct()
        .all()
    )

    return [category[0] for category in categories]


def search_products(db: Session, query: str):
    query = query.strip().lower()

    if len(query) < 3:
        return []

    products = (
        db.query(Product)
        .options(selectinload(Product.items))
        .all()
    )

    results = []

    for product in products:
        score = fuzz.WRatio(query, product.name.lower())

        if score >= 65:
            results.append((product, score))

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return [product for product, _score in results]


def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .options(selectinload(Product.items))
        .filter(Product.id == product_id)
        .first()
    )
