from fastapi import FastAPI

from app.core.cors import setup_cors
from app.db.database import Base, engine

from app.models.user import User
from app.models.product import Product, ProductItem
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatusHistory

from app.routes.contact import router as contact_router
from app.routes.auth import router as auth_router

from app.routes.assets import router as assets_router
from app.routes.products import router as products_router
from app.routes.cart import router as cart_router
from app.routes.favorite import router as favorites_router
from app.routes.rating import router as rating_router

from app.routes.orders import router as orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

setup_cors(app)

app.include_router(contact_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(rating_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"} 