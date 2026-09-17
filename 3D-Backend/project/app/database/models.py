"""Re-export every model so Alembic and the app see them from one place.

Importing ``app.database.models`` registers all mapped tables on ``Base.metadata``.
"""

from app.models.user import User
from app.models.avatar import Avatar
from app.models.clothing import Clothing
from app.models.outfit import Outfit, OutfitItem

__all__ = ["User", "Avatar", "Clothing", "Outfit", "OutfitItem"]
