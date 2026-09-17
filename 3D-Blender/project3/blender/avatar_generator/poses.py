"""
Pose presets for the avatar armature.

Poses are stored as dicts mapping bone names to Euler rotation tuples
in degrees.  ``apply_idle_pose`` and ``reset_pose`` are convenience
wrappers around ``armature.apply_pose``.
"""

from __future__ import annotations

import bpy
import math
from typing import Optional

from .armature import apply_pose


def reset_pose(armature_name: str = "Armature") -> None:
    """Return every bone to its rest rotation (standing T-pose)."""
    armature = bpy.data.objects.get(armature_name)
    if armature is not None:
        apply_pose(armature, "standing")


def apply_idle_pose(armature_name: str = "Armature") -> None:
    """Apply a relaxed idle pose — slight arm bend and head tilt."""
    armature = bpy.data.objects.get(armature_name)
    if armature is not None:
        apply_pose(armature, "idle")
