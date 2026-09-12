from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse

from app.services.supabase_storage_service import upload_file
from app.core.supabase_client import (
    supabase_client,
    SUPABASE_BUCKET_NAME
)


router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/upload")
def upload_asset(file: UploadFile = File(...)):
    file_path = upload_file(file)

    return {
        "message": "File uploaded successfully",
        "file_path": file_path
    }


@router.get("/{file_path:path}")
def get_asset(file_path: str):
    try:
        public_url = (
            supabase_client
            .storage
            .from_(SUPABASE_BUCKET_NAME)
            .get_public_url(file_path)
        )

        return RedirectResponse(url=public_url)

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )
