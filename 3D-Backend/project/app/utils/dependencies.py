"""Shared FastAPI dependencies — DB session and current-user extraction."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.models.user import User
from app.utils.security import decode_token

logger = logging.getLogger(__name__)

# tokenUrl is the relative path Swagger uses for the "Authorize" form
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_token(token)
    if token_data is None or token_data.user_id is None:
        raise credentials_exc

    user = db.get(User, token_data.user_id)
    if user is None:
        logger.warning("Token referenced non-existent user_id=%s", token_data.user_id)
        raise credentials_exc
    return user
