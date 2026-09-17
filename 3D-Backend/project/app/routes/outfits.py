"""Outfit CRUD routes — users manage outfits built from clothing items on their avatars."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.clothing import Clothing
from app.models.outfit import Outfit, OutfitItem
from app.models.user import User
from app.schemas.outfit import OutfitCreate, OutfitOut, OutfitUpdate
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outfits", tags=["outfits"])


def _get_owned_outfit(outfit_id: int, user: User, db: Session) -> Outfit:
    outfit = db.get(Outfit, outfit_id)
    if outfit is None or outfit.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    return outfit


def _validate_avatar_owned(avatar_id: int, user: User, db: Session) -> None:
    owned = db.scalar(select(Outfit).where(Outfit.avatar_id == avatar_id, Outfit.user_id == user.id))
    # Simpler: check the avatar table directly
    from app.models.avatar import Avatar
    avatar = db.get(Avatar, avatar_id)
    if avatar is None or avatar.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")


def _replace_items(outfit: Outfit, item_clothing_ids: list[int], db: Session) -> None:
    # Wipe existing items then re-create from the incoming list
    outfit.items.clear()
    db.flush()
    for clothing_id in item_clothing_ids:
        clothing = db.get(Clothing, clothing_id)
        if clothing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Clothing item {clothing_id} not found")
        outfit.items.append(OutfitItem(clothing_id=clothing_id))


@router.post("", response_model=OutfitOut, status_code=status.HTTP_201_CREATED)
def create_outfit(
    payload: OutfitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_avatar_owned(payload.avatar_id, current_user, db)
    outfit = Outfit(user_id=current_user.id, avatar_id=payload.avatar_id, name=payload.name)
    db.add(outfit)
    db.flush()  # populate outfit.id before adding children
    _replace_items(outfit, [i.clothing_id for i in payload.items], db)
    db.commit()
    db.refresh(outfit)
    logger.info("Created outfit id=%s for user=%s", outfit.id, current_user.id)
    return outfit


@router.get("", response_model=list[OutfitOut])
def list_outfits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(
        select(Outfit).where(Outfit.user_id == current_user.id).order_by(Outfit.created_at.desc())
    ).all()


@router.get("/{outfit_id}", response_model=OutfitOut)
def get_outfit(outfit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_owned_outfit(outfit_id, current_user, db)


@router.put("/{outfit_id}", response_model=OutfitOut)
def update_outfit(
    outfit_id: int,
    payload: OutfitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    outfit = _get_owned_outfit(outfit_id, current_user, db)
    data = payload.model_dump(exclude_unset=True)

    items = data.pop("items", None)
    if "avatar_id" in data:
        _validate_avatar_owned(data["avatar_id"], current_user, db)
    for field, value in data.items():
        setattr(outfit, field, value)
    if items is not None:
        _replace_items(outfit, [i.clothing_id for i in items], db)
    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(outfit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    outfit = _get_owned_outfit(outfit_id, current_user, db)
    db.delete(outfit)
    db.commit()
    logger.info("Deleted outfit id=%s for user=%s", outfit_id, current_user.id)
    return None
