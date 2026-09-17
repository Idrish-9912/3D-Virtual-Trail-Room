"""Outfit schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.clothing import ClothingOut


class OutfitItemCreate(BaseModel):
    clothing_id: int


class OutfitItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clothing_id: int
    clothing: ClothingOut


class OutfitCreate(BaseModel):
    avatar_id: int
    name: str = Field(..., min_length=1, max_length=150)
    items: list[OutfitItemCreate] = Field(default_factory=list)


class OutfitUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    avatar_id: int | None = None
    items: list[OutfitItemCreate] | None = None


class OutfitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    avatar_id: int
    name: str
    created_at: datetime
    items: list[OutfitItemOut]
