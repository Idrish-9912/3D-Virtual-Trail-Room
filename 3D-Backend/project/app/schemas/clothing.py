"""Clothing schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClothingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    category: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    model_url: str | None = Field(None, max_length=512)
    thumbnail_url: str | None = Field(None, max_length=512)


class ClothingCreate(ClothingBase):
    pass


class ClothingOut(ClothingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
