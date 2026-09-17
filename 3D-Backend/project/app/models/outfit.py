"""Outfit + OutfitItem models.

An outfit groups multiple clothing items onto an avatar. The many-to-many
relationship between outfits and clothing is modelled explicitly through
``OutfitItem`` so callers can control ordering and add metadata later.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    avatar_id: Mapped[int] = mapped_column(
        ForeignKey("avatars.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", backref="outfits")
    avatar = relationship("Avatar", backref="outfits")
    items = relationship(
        "OutfitItem", back_populates="outfit", cascade="all, delete-orphan", order_by="OutfitItem.id"
    )


class OutfitItem(Base):
    __tablename__ = "outfit_items"
    __table_args__ = (UniqueConstraint("outfit_id", "clothing_id", name="uq_outfit_clothing"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    outfit_id: Mapped[int] = mapped_column(
        ForeignKey("outfits.id", ondelete="CASCADE"), index=True, nullable=False
    )
    clothing_id: Mapped[int] = mapped_column(
        ForeignKey("clothing.id", ondelete="CASCADE"), index=True, nullable=False
    )

    outfit = relationship("Outfit", back_populates="items")
    clothing = relationship("Clothing", back_populates="outfit_items")
