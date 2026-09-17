"""Generic upload response schema."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    url: str
