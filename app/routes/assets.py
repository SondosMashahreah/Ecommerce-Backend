from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from minio.error import S3Error

from app.services.minio_service import upload_file
from app.core.minio_client import minio_client, MINIO_BUCKET_NAME


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
        response = minio_client.get_object(
            MINIO_BUCKET_NAME,
            file_path
        )

        return StreamingResponse(
            response,
            media_type=response.headers.get(
                "Content-Type",
                "application/octet-stream"
            )
        )

    except S3Error:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )