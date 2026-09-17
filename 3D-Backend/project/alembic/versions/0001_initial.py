"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "avatars",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("skin_color", sa.String(32)),
        sa.Column("hair_style", sa.String(64)),
        sa.Column("hair_color", sa.String(32)),
        sa.Column("face_shape", sa.String(64)),
        sa.Column("body_type", sa.String(64)),
        sa.Column("model_url", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_avatars_user_id", "avatars", ["user_id"])

    op.create_table(
        "clothing",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("model_url", sa.String(512)),
        sa.Column("thumbnail_url", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_clothing_category", "clothing", ["category"])

    op.create_table(
        "outfits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("avatar_id", sa.Integer(), sa.ForeignKey("avatars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outfits_user_id", "outfits", ["user_id"])
    op.create_index("ix_outfits_avatar_id", "outfits", ["avatar_id"])

    op.create_table(
        "outfit_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("outfit_id", sa.Integer(), sa.ForeignKey("outfits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clothing_id", sa.Integer(), sa.ForeignKey("clothing.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("outfit_id", "clothing_id", name="uq_outfit_clothing"),
    )
    op.create_index("ix_outfit_items_outfit_id", "outfit_items", ["outfit_id"])
    op.create_index("ix_outfit_items_clothing_id", "outfit_items", ["clothing_id"])


def downgrade() -> None:
    op.drop_index("ix_outfit_items_clothing_id", table_name="outfit_items")
    op.drop_index("ix_outfit_items_outfit_id", table_name="outfit_items")
    op.drop_table("outfit_items")

    op.drop_index("ix_outfits_avatar_id", table_name="outfits")
    op.drop_index("ix_outfits_user_id", table_name="outfits")
    op.drop_table("outfits")

    op.drop_index("ix_clothing_category", table_name="clothing")
    op.drop_table("clothing")

    op.drop_index("ix_avatars_user_id", table_name="avatars")
    op.drop_table("avatars")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
