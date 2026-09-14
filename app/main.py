from fastapi import FastAPI

from app.core.cors import setup_cors
from app.db.database import Base, engine

from app.models.user import User
from app.models.product import Product, ProductItem
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatusHistory

from app.routes.admin_coupons import router as admin_coupons_router
from app.routes.admin_reviews import router as admin_reviews_router

from app.routes.contact import router as contact_router
from app.routes.auth import router as auth_router

from app.routes.assets import router as assets_router
from app.routes.products import router as products_router
from app.routes.cart import router as cart_router
from app.routes.favorite import router as favorites_router
from app.routes.rating import router as rating_router
from app.routes.coupons import router as coupons_router

from app.routes.orders import router as orders_router

from app.routes.admin import (
    router as admin_router
)

from app.routes.admin_products import (
    router as admin_products_router
)

from app.routes.admin_orders import (
    router as admin_orders_router,
)

from app.routes.admin_customers import (
    router as admin_customers_router,
)

from app.routes.admin_messages import (
    router as admin_messages_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

setup_cors(app)

app.include_router(
    admin_products_router,
    prefix="/api/v1"
)

app.include_router(admin_coupons_router, prefix="/api/v1")
app.include_router(admin_reviews_router, prefix="/api/v1")

app.include_router(contact_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(rating_router, prefix="/api/v1")
app.include_router(coupons_router, prefix="/api/v1")
app.include_router(admin_router,prefix="/api/v1")
app.include_router(admin_orders_router, prefix="/api/v1")
app.include_router(admin_customers_router, prefix="/api/v1")
app.include_router(admin_messages_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"} 
