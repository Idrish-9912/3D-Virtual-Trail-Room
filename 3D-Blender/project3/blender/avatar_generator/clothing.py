"""
Clothing system.

Each clothing piece is a separate mesh object built to fit over the
base avatar.  Every piece is parented to the same armature as the body
so it deforms correctly during animation.

Clothing pieces
---------------
    T-shirt  — short-sleeve top covering torso + upper arms
    Shirt    — long-sleeve button-down
    Jacket   — heavier long-sleeve outer layer
    Pants    — covers both legs
    Shoes     — covers the feet

All clothing uses the Armature modifier + automatic weight painting
inherited from ``parent_mesh_to_armature``.
"""

from __future__ import annotations

import bpy
import math
from typing import Optional

from .config import AvatarConfig, OutfitType
from .materials import create_material, _assign_material
from .armature import parent_mesh_to_armature


# ---------------------------------------------------------------------------
# Primitive helpers (local to clothing)
# ---------------------------------------------------------------------------

def _add_cylinder(name, location, radius, depth, rotation=(0, 0, 0), vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth,
        location=location, rotation=rotation,
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj


def _add_cube(name, location, size, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    return obj


# ---------------------------------------------------------------------------
# Clothing builders
# ---------------------------------------------------------------------------

def _build_tshirt(config: AvatarConfig) -> bpy.types.Object:
    """T-shirt: torso shell + short sleeves on upper arms."""
    torso = _add_cube("Cloth_TShirt_Torso", (0, 0, 1.07), (0.24, 0.14, 0.32))
    sleeve_l = _add_cylinder("Cloth_TShirt_SleeveL", (0.28, 0, 1.25), 0.055, 0.12,
                             rotation=(0, math.radians(90), 0))
    sleeve_r = _add_cylinder("Cloth_TShirt_SleeveR", (-0.28, 0, 1.25), 0.055, 0.12,
                            rotation=(0, math.radians(90), 0))
    return _join_clothing([torso, sleeve_l, sleeve_r], "Cloth_TShirt")


def _build_shirt(config: AvatarConfig) -> bpy.types.Object:
    """Long-sleeve button-down shirt."""
    torso = _add_cube("Cloth_Shirt_Torso", (0, 0, 1.07), (0.24, 0.14, 0.32))
    sleeve_l_upper = _add_cylinder("Cloth_Shirt_UL", (0.28, 0, 1.25), 0.052, 0.26,
                                   rotation=(0, math.radians(90), 0))
    sleeve_l_lower = _add_cylinder("Cloth_Shirt_FL", (0.48, 0, 1.17), 0.046, 0.24,
                                   rotation=(0, math.radians(90), 0))
    sleeve_r_upper = _add_cylinder("Cloth_Shirt_UR", (-0.28, 0, 1.25), 0.052, 0.26,
                                   rotation=(0, math.radians(90), 0))
    sleeve_r_lower = _add_cylinder("Cloth_Shirt_FR", (-0.48, 0, 1.17), 0.046, 0.24,
                                   rotation=(0, math.radians(90), 0))
    return _join_clothing([torso, sleeve_l_upper, sleeve_l_lower,
                           sleeve_r_upper, sleeve_r_lower], "Cloth_Shirt")


def _build_jacket(config: AvatarConfig) -> bpy.types.Object:
    """Heavier outer jacket — slightly larger than the shirt."""
    torso = _add_cube("Cloth_Jacket_Torso", (0, 0, 1.06), (0.27, 0.16, 0.34))
    sleeve_l_upper = _add_cylinder("Cloth_Jacket_UL", (0.29, 0, 1.24), 0.060, 0.26,
                                   rotation=(0, math.radians(90), 0))
    sleeve_l_lower = _add_cylinder("Cloth_Jacket_FL", (0.49, 0, 1.16), 0.054, 0.24,
                                   rotation=(0, math.radians(90), 0))
    sleeve_r_upper = _add_cylinder("Cloth_Jacket_UR", (-0.29, 0, 1.24), 0.060, 0.26,
                                   rotation=(0, math.radians(90), 0))
    sleeve_r_lower = _add_cylinder("Cloth_Jacket_FR", (-0.49, 0, 1.16), 0.054, 0.24,
                                   rotation=(0, math.radians(90), 0))
    return _join_clothing([torso, sleeve_l_upper, sleeve_l_lower,
                           sleeve_r_upper, sleeve_r_lower], "Cloth_Jacket")


def _build_pants(config: AvatarConfig) -> bpy.types.Object:
    """Pants covering both legs."""
    leg_l_upper = _add_cylinder("Cloth_Pants_UL", (0.10, 0, 0.69), 0.068, 0.42)
    leg_l_lower = _add_cylinder("Cloth_Pants_LL", (0.10, 0, 0.29), 0.058, 0.42)
    leg_r_upper = _add_cylinder("Cloth_Pants_UR", (-0.10, 0, 0.69), 0.068, 0.42)
    leg_r_lower = _add_cylinder("Cloth_Pants_LR", (-0.10, 0, 0.29), 0.058, 0.42)
    return _join_clothing([leg_l_upper, leg_l_lower, leg_r_upper, leg_r_lower],
                          "Cloth_Pants")


def _build_shoes(config: AvatarConfig) -> bpy.types.Object:
    """Shoes covering the feet."""
    shoe_l = _add_cube("Cloth_ShoeL", (0.10, 0.06, 0.045), (0.085, 0.18, 0.06))
    shoe_r = _add_cube("Cloth_ShoeR", (-0.10, 0.06, 0.045), (0.085, 0.18, 0.06))
    return _join_clothing([shoe_l, shoe_r], "Cloth_Shoes")


# ---------------------------------------------------------------------------
# Outfit application
# ---------------------------------------------------------------------------

_CLOTH_BUILDERS = {
    OutfitType.TSHIRT: _build_tshirt,
    OutfitType.SHIRT: _build_shirt,
    OutfitType.JACKET: _build_jacket,
    OutfitType.PANTS: _build_pants,
    OutfitType.SHOES: _build_shoes,
}

_CLOTH_MATERIALS = {
    OutfitType.TSHIRT: ("M_TShirt", "clothing_color"),
    OutfitType.SHIRT: ("M_Shirt", "clothing_color"),
    OutfitType.JACKET: ("M_Jacket", "clothing_color"),
    OutfitType.PANTS: ("M_Pants", "pants_color"),
    OutfitType.SHOES: ("M_Shoes", "shoe_color"),
}


def apply_outfit(config: AvatarConfig) -> list[bpy.types.Object]:
    """Build and attach every clothing piece in ``config.outfit_pieces``.

    Returns the list of created clothing objects.
    """
    armature = bpy.data.objects.get(config.armature_name or "Armature")
    created: list[bpy.types.Object] = []

    for piece_type in config.outfit_pieces:
        builder = _CLOTH_BUILDERS.get(piece_type)
        if builder is None:
            continue

        obj = builder(config)

        # Material
        mat_name, color_attr = _CLOTH_MATERIALS.get(piece_type, ("M_Clothing", "clothing_color"))
        color = getattr(config, color_attr, (0.5, 0.5, 0.5, 1.0))
        mat = create_material(mat_name, color, roughness=0.65)
        _assign_material(obj, mat)

        # Parent to armature so clothing deforms with the skeleton.
        if armature is not None:
            parent_mesh_to_armature(obj, armature, subdivide=False)

        created.append(obj)

    return created


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _join_clothing(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    """Join clothing sub-meshes into a single object."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = name
    return joined
