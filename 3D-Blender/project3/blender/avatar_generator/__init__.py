"""
avatar_generator package
========================

A modular Blender Python toolkit for building a customizable,
stylized Bitmoji-style 3D humanoid avatar.

Public API
----------
    from avatar_generator import (
        create_base_avatar,
        create_material,
        set_skin_color,
        set_hair_color,
        change_face_shape,
        change_body_type,
        apply_outfit,
        export_avatar,
    )

Every public function accepts an ``AvatarConfig`` dataclass so that
future AI-generated parameters can be passed straight into the script.
"""

from .config import AvatarConfig, BodyType, HairStyle, FaceShape, OutfitType
from .materials import create_material, set_skin_color, set_hair_color
from .base_avatar import create_base_avatar
from .customization import change_face_shape, change_body_type
from .armature import add_armature, apply_pose
from .clothing import apply_outfit
from .poses import apply_idle_pose, reset_pose
from .export import export_avatar

__all__ = [
    "AvatarConfig",
    "BodyType",
    "HairStyle",
    "FaceShape",
    "OutfitType",
    "create_base_avatar",
    "create_material",
    "set_skin_color",
    "set_hair_color",
    "change_face_shape",
    "change_body_type",
    "add_armature",
    "apply_pose",
    "apply_outfit",
    "apply_idle_pose",
    "reset_pose",
    "export_avatar",
]
