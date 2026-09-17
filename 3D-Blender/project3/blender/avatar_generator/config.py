"""
Configuration dataclasses and enums.

These are the single source of truth for every parameter the avatar
generator understands.  An AI pipeline (or a human) can build an
``AvatarConfig`` object and pass it to ``create_base_avatar`` / the
customization helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BodyType(str, Enum):
    """Overall body proportions."""
    SLIM = "slim"
    AVERAGE = "average"
    ATHLETIC = "athletic"


class HairStyle(str, Enum):
    """Hair mesh variants."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    BUZZ = "buzz"
    BOB = "bob"


class FaceShape(str, Enum):
    """Face-silhouette presets (driven by shape keys)."""
    OVAL = "oval"
    ROUND = "round"
    SQUARE = "square"
    HEART = "heart"


class OutfitType(str, Enum):
    """Clothing preset identifiers."""
    TSHIRT = "tshirt"
    SHIRT = "shirt"
    JACKET = "jacket"
    PANTS = "pants"
    SHOES = "shoes"


@dataclass
class AvatarConfig:
    """All parameters needed to build and customize one avatar.

    Defaults produce a friendly, average-build avatar with short brown
    hair, a medium skin tone, and a t-shirt + pants outfit.
    """

    # --- identity / naming -----------------------------------------------
    name: str = "Avatar"

    # --- colors ----------------------------------------------------------
    skin_color: tuple[float, float, float, float] = (0.96, 0.78, 0.66, 1.0)
    hair_color: tuple[float, float, float, float] = (0.20, 0.12, 0.06, 1.0)
    eye_color: tuple[float, float, float, float] = (0.20, 0.35, 0.60, 1.0)
    clothing_color: tuple[float, float, float, float] = (0.25, 0.45, 0.70, 1.0)
    pants_color: tuple[float, float, float, float] = (0.18, 0.18, 0.22, 1.0)
    shoe_color: tuple[float, float, float, float] = (0.12, 0.12, 0.14, 1.0)

    # --- structural presets ---------------------------------------------
    body_type: BodyType = BodyType.AVERAGE
    hair_style: HairStyle = HairStyle.SHORT
    face_shape: FaceShape = FaceShape.OVAL

    # --- shape-key slider values (0.0 – 1.0) -----------------------------
    face_width: float = 0.50
    jaw_width: float = 0.50
    cheek_size: float = 0.50
    eye_size: float = 0.50

    # --- outfit selection ------------------------------------------------
    outfit_pieces: list[OutfitType] = field(
        default_factory=lambda: [OutfitType.TSHIRT, OutfitType.PANTS, OutfitType.SHOES]
    )

    # --- export ----------------------------------------------------------
    export_path: str = "blender/output/avatar.glb"

    # --- internal (set during build, not user-facing) --------------------
    # Reference to the created armature object so other helpers can find it.
    armature_name: Optional[str] = None
