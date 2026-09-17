"""
Customization functions.

These helpers mutate an already-built avatar by adjusting shape keys
and materials.  They are safe to call multiple times.
"""

from __future__ import annotations

import bpy
from typing import Optional

from .config import AvatarConfig, BodyType, FaceShape
from .materials import _set_color
from .base_avatar import _apply_body_type_keys, _apply_face_shape_keys


def change_face_shape(config: AvatarConfig, face_shape: FaceShape) -> None:
    """Change the face silhouette preset and re-apply slider values."""
    config.face_shape = face_shape
    body = bpy.data.objects.get("Avatar_Body")
    if body is not None:
        _apply_face_shape_keys(body, face_shape, config)


def change_body_type(config: AvatarConfig, body_type: BodyType) -> None:
    """Change the overall body proportions via shape keys."""
    config.body_type = body_type
    body = bpy.data.objects.get("Avatar_Body")
    if body is not None:
        _apply_body_type_keys(body, body_type)


def set_eye_color(config: AvatarConfig, color: tuple[float, float, float, float]) -> None:
    """Change the eye material's base color."""
    config.eye_color = color
    _set_color("M_Eyes", color)


def change_hair_style(config: AvatarConfig, hair_style) -> None:
    """Change the hair style by adjusting the hair mesh scale.

    A full rebuild would give the best results; here we scale the
    existing hair mesh as a lightweight approximation.
    """
    from .config import HairStyle

    if isinstance(hair_style, str):
        hair_style = HairStyle(hair_style)
    config.hair_style = hair_style

    hair = bpy.data.objects.get("Avatar_Hair")
    if hair is not None:
        scales = {
            HairStyle.SHORT:  (1.05, 1.05, 1.10),
            HairStyle.MEDIUM: (1.08, 1.12, 1.20),
            HairStyle.LONG:   (1.10, 1.20, 1.35),
            HairStyle.BUZZ:   (1.02, 1.02, 1.04),
            HairStyle.BOB:    (1.12, 1.15, 1.18),
        }
        sx, sy, sz = scales.get(hair_style, scales[HairStyle.SHORT])
        hair.scale = (sx, sy, sz)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = hair
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
