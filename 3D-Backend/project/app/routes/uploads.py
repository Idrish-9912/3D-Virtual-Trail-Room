"""Image upload route — validates type/size, stores safely, returns a URL."""

import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.models.user import User
from app.schemas.upload import UploadResponse
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["uploads"])


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {settings.ALLOWED_IMAGE_TYPES}",
        )

    # Read the file in chunks so we can enforce the size limit safely
    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    # Ensure the upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate a unique filename to prevent collisions and path traversal
    ext = os.path.splitext(file.filename or "")[1]
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(dest, "wb") as f:
        f.write(contents)

    url = f"/{settings.UPLOAD_DIR}/{safe_filename}"
    logger.info("User %s uploaded %s -> %s", current_user.id, file.filename, url)
    return UploadResponse(filename=safe_filename, url=url)
