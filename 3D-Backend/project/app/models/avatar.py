"""Avatar model — a user's personalized 3D mannequin configuration."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    skin_color: Mapped[str | None] = mapped_column(String(32))
    hair_style: Mapped[str | None] = mapped_column(String(64))
    hair_color: Mapped[str | None] = mapped_column(String(32))
    face_shape: Mapped[str | None] = mapped_column(String(64))
    body_type: Mapped[str | None] = mapped_column(String(64))
    model_url: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Back-reference to the owning user (no circular import needed: string ref)
    user = relationship("User", backref="avatars")
