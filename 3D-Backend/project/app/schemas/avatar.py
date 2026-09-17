"""Avatar schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AvatarBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    skin_color: str | None = Field(None, max_length=32)
    hair_style: str | None = Field(None, max_length=64)
    hair_color: str | None = Field(None, max_length=32)
    face_shape: str | None = Field(None, max_length=64)
    body_type: str | None = Field(None, max_length=64)
    model_url: str | None = Field(None, max_length=512)


class AvatarCreate(AvatarBase):
    pass


class AvatarUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    skin_color: str | None = None
    hair_style: str | None = None
    hair_color: str | None = None
    face_shape: str | None = None
    body_type: str | None = None
    model_url: str | None = None


class AvatarOut(AvatarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
