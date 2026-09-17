"""Avatar CRUD routes — users can only access their own avatars."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.avatar import Avatar
from app.models.user import User
from app.schemas.avatar import AvatarCreate, AvatarOut, AvatarUpdate
from app.utils.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avatars", tags=["avatars"])


def _get_owned_avatar(avatar_id: int, user: User, db: Session) -> Avatar:
    avatar = db.get(Avatar, avatar_id)
    if avatar is None or avatar.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return avatar


@router.post("", response_model=AvatarOut, status_code=status.HTTP_201_CREATED)
def create_avatar(
    payload: AvatarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    avatar = Avatar(user_id=current_user.id, **payload.model_dump())
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    logger.info("Created avatar id=%s for user=%s", avatar.id, current_user.id)
    return avatar


@router.get("", response_model=list[AvatarOut])
def list_avatars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Avatar).where(Avatar.user_id == current_user.id).order_by(Avatar.created_at.desc())).all()


@router.get("/{avatar_id}", response_model=AvatarOut)
def get_avatar(avatar_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_owned_avatar(avatar_id, current_user, db)


@router.put("/{avatar_id}", response_model=AvatarOut)
def update_avatar(
    avatar_id: int,
    payload: AvatarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    avatar = _get_owned_avatar(avatar_id, current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(avatar, field, value)
    db.commit()
    db.refresh(avatar)
    return avatar


@router.delete("/{avatar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(avatar_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    avatar = _get_owned_avatar(avatar_id, current_user, db)
    db.delete(avatar)
    db.commit()
    logger.info("Deleted avatar id=%s for user=%s", avatar_id, current_user.id)
    return None
