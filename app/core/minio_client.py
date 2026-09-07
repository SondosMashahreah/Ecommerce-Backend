import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME = os.getenv(
    "MINIO_BUCKET_NAME",
    "ecommerce-assets"
)

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)