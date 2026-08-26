import logging

from app.db.database import Base, engine
from app.models.contact import Contact


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)

logger.info("Tables created successfully!")