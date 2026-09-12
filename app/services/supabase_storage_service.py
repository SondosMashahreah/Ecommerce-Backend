import os
import uuid

from fastapi import UploadFile

from app.core.supabase_client import (
    supabase_client,
    SUPABASE_BUCKET_NAME
)


def upload_file(file: UploadFile, folder: str = "products") -> str:
    extension = os.path.splitext(file.filename)[1]

    unique_filename = f"{uuid.uuid4()}{extension}"
    object_name = f"{folder}/{unique_filename}"

    file_content = file.file.read()

    supabase_client.storage.from_(SUPABASE_BUCKET_NAME).upload(
        path=object_name,
        file=file_content,
        file_options={
            "content-type": file.content_type or "application/octet-stream",
            "upsert": "false"
        }
    )

    return object_name
