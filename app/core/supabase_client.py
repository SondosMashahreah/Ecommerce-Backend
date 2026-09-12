import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
SUPABASE_BUCKET_NAME = os.getenv(
    "SUPABASE_BUCKET_NAME",
    "ecommerce-assets"
)

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not configured")

if not SUPABASE_SECRET_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY is not configured")

supabase_client: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)
