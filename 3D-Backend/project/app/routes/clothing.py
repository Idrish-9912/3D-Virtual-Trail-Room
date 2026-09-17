"""Clothing catalog routes — read-only for clients."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.clothing import Clothing
from app.models.user import User
from app.schemas.clothing import ClothingOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/clothing", tags=["clothing"])


@router.get("", response_model=list[ClothingOut])
def list_clothing(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Clothing).order_by(Clothing.created_at.desc()).offset(skip).limit(limit)).all()


@router.get("/{clothing_id}", response_model=ClothingOut)
def get_clothing(
    clothing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.get(Clothing, clothing_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found")
    return item


@router.get("/category/{category}", response_model=list[ClothingOut])
def get_clothing_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Clothing).where(Clothing.category == category).order_by(Clothing.created_at.desc())
    ).all()
