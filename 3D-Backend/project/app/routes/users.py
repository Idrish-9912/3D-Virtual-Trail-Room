"""User profile routes — read/update the authenticated user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut, deprecated=True)
def me(current_user: User = Depends(get_current_user)):
    """Alias for /api/auth/me — kept for convenience."""
    return current_user
