from io import BytesIO
import os
import uuid

from fastapi import UploadFile

from app.core.minio_client import (
    minio_client,
    MINIO_BUCKET_NAME
)


def upload_file(file: UploadFile, folder: str = "products") -> str:
    extension = os.path.splitext(file.filename)[1]

    unique_filename = f"{uuid.uuid4()}{extension}"

    object_name = f"{folder}/{unique_filename}"

    file_content = file.file.read()

    minio_client.put_object(
        bucket_name=MINIO_BUCKET_NAME,
        object_name=object_name,
        data=BytesIO(file_content),
        length=len(file_content),
        content_type=file.content_type
    )

    return object_name  