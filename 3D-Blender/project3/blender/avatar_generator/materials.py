"""
Material helpers.

All avatar materials use the Principled BSDF shader so they export
cleanly to glTF / GLB.  Colors are stored as linear RGBA floats.
"""

from __future__ import annotations

import bpy
from typing import Optional

from .config import AvatarConfig


def create_material(
    name: str,
    base_color: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    roughness: float = 0.55,
    metallic: float = 0.0,
) -> bpy.types.Material:
    """Create (or replace) a Principled BSDF material and return it.

    Parameters
    ----------
    name : str
        Unique material name.  If a material with this name already
        exists it is overwritten so the function is idempotent.
    base_color : tuple
        Linear RGBA floats in 0–1 range.
    roughness : float
        0 = mirror, 1 = matte.
    metallic : float
        0 = dielectric, 1 = metal.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    # Wipe any stale nodes from a previous run.
    mat.node_tree.nodes.clear()

    output = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")

    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def _set_color(material_name: str, color: tuple[float, float, float, float]) -> None:
    """Update the Base Color of an existing material by name."""
    mat = bpy.data.materials.get(material_name)
    if mat is None or mat.node_tree is None:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color


def set_skin_color(config: AvatarConfig, color: tuple[float, float, float, float]) -> None:
    """Change the skin material's base color."""
    config.skin_color = color
    _set_color("M_Skin", color)


def set_hair_color(config: AvatarConfig, color: tuple[float, float, float, float]) -> None:
    """Change the hair material's base color."""
    config.hair_color = color
    _set_color("M_Hair", color)


def _assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    """Assign *material* to every polygon of *obj*."""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
