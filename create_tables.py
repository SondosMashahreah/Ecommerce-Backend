import logging

from app.db.database import Base, engine
from app.models.contact import Contact
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.models.favorite import Favorite
from app.models.rating import Rating


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)
logger.info("Tables created successfully!")