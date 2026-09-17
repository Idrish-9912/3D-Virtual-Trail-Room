"""
Export utilities.

``export_avatar`` exports the entire avatar (body, hair, clothing, and
armature) as a single GLB file optimized for web / React Three Fiber.
"""

from __future__ import annotations

import bpy
import os
from typing import Optional

from .config import AvatarConfig


def export_avatar(config: AvatarConfig, path: Optional[str] = None) -> str:
    """Export the avatar scene to a GLB file and return the file path.

    Parameters
    ----------
    config : AvatarConfig
        The config used to build the avatar (``export_path`` is read
        from here unless *path* is given).
    path : str, optional
        Override the export path from *config*.
    """
    export_path = path or config.export_path
    _ensure_dir(export_path)

    # Select only avatar-related objects so the GLB stays lean.
    avatar_prefixes = ("Avatar_", "Cloth_", "Armature")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.name.startswith(avatar_prefixes) or obj.name == "Armature":
            obj.select_set(True)

    # glTF 2.0 export settings — web-optimized.
    export_kwargs = dict(
        filepath=export_path,
        use_selection=True,
        export_format="GLB",
        export_apply=True,            # apply modifiers on export
        export_yup=True,              # Three.js expects Y-up
        export_materials="EXPORT",
        export_colors=True,
        export_cameras=False,
        export_lights=False,
        export_extras=False,
        export_animations=False,      # no baked animations yet
    )

    # Blender 4.x renamed some export kwargs; try the modern signature
    # first and fall back to the 3.x-compatible version.
    try:
        bpy.ops.export_scene.gltf(**export_kwargs)
    except TypeError:
        export_kwargs.pop("export_materials", None)
        export_kwargs.pop("export_extras", None)
        bpy.ops.export_scene.gltf(**export_kwargs)

    return export_path


def _ensure_dir(file_path: str) -> None:
    """Create the parent directory of *file_path* if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
