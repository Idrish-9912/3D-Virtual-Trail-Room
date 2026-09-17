"""
Armature creation and parenting utilities.

A single humanoid rig (``Armature``) is created with the bones listed in
``BONE_HIERARCHY``.  Every avatar and clothing mesh is parented to this
armature so they share the same skeleton and deform together during
animation.
"""

from __future__ import annotations

import bpy
from mathutils import Vector
from typing import Optional

# (bone_name, parent_name, head, tail)
# Coordinates are in avatar-local space (meters).  The avatar stands
# ~1.75 m tall, feet on the ground plane (z = 0).
BONE_HIERARCHY: list[tuple[str, Optional[str], Vector, Vector]] = [
    # --- hips & spine --------------------------------------------------
    ("Hips",       None,         Vector((0, 0, 0.90)),  Vector((0, 0, 1.00))),
    ("Spine",      "Hips",       Vector((0, 0, 1.00)),  Vector((0, 0, 1.15))),
    ("Chest",      "Spine",      Vector((0, 0, 1.15)),  Vector((0, 0, 1.32))),
    ("Neck",       "Chest",      Vector((0, 0, 1.32)),  Vector((0, 0, 1.42))),
    ("Head",       "Neck",       Vector((0, 0, 1.42)),  Vector((0, 0, 1.62))),
    # --- left arm ------------------------------------------------------
    ("Shoulder.L", "Chest",      Vector((0.06, 0, 1.30)), Vector((0.16, 0, 1.28))),
    ("UpperArm.L", "Shoulder.L", Vector((0.16, 0, 1.28)), Vector((0.40, 0, 1.22))),
    ("ForeArm.L",  "UpperArm.L", Vector((0.40, 0, 1.22)), Vector((0.60, 0, 1.12))),
    ("Hand.L",     "ForeArm.L",  Vector((0.60, 0, 1.12)), Vector((0.72, 0, 1.06))),
    # --- right arm -----------------------------------------------------
    ("Shoulder.R", "Chest",      Vector((-0.06, 0, 1.30)), Vector((-0.16, 0, 1.28))),
    ("UpperArm.R", "Shoulder.R", Vector((-0.16, 0, 1.28)), Vector((-0.40, 0, 1.22))),
    ("ForeArm.R",  "UpperArm.R", Vector((-0.40, 0, 1.22)), Vector((-0.60, 0, 1.12))),
    ("Hand.R",     "ForeArm.R",  Vector((-0.60, 0, 1.12)), Vector((-0.72, 0, 1.06))),
    # --- left leg ------------------------------------------------------
    ("UpperLeg.L", "Hips",       Vector((0.10, 0, 0.88)), Vector((0.10, 0, 0.50))),
    ("LowerLeg.L", "UpperLeg.L", Vector((0.10, 0, 0.50)), Vector((0.10, 0, 0.08))),
    ("Foot.L",     "LowerLeg.L", Vector((0.10, 0, 0.08)), Vector((0.10, 0.12, 0.02))),
    # --- right leg -----------------------------------------------------
    ("UpperLeg.R", "Hips",       Vector((-0.10, 0, 0.88)), Vector((-0.10, 0, 0.50))),
    ("LowerLeg.R", "UpperLeg.R", Vector((-0.10, 0, 0.50)), Vector((-0.10, 0, 0.08))),
    ("Foot.R",     "LowerLeg.R", Vector((-0.10, 0, 0.08)), Vector((-0.10, 0.12, 0.02))),
]


def add_armature(name: str = "Armature") -> bpy.types.Object:
    """Create the humanoid armature and return the armature object.

    The rig is built in EDIT mode so bone parenting and lengths are
    correct from the start.  All bones use ``head = tail of parent`` so
    the hierarchy is a clean chain.
    """
    arm_data = bpy.data.armatures.new(name=f"{name}_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.collection.objects.link(arm_obj)

    # Enter edit mode to create bones.
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = arm_data.edit_bones
    bone_map: dict[str, bpy.types.EditBone] = {}

    for bone_name, parent_name, head, tail in BONE_HIERARCHY:
        b = edit_bones.new(bone_name)
        b.head = head
        b.tail = tail
        if parent_name is not None:
            b.parent = bone_map[parent_name]
        bone_map[bone_name] = b

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def apply_pose(armature: bpy.types.Object, pose_name: str = "standing") -> None:
    """Apply a named pose to the armature.

    Currently supports ``"standing"`` (reset) and ``"idle"`` (slight arm
    and leg offset).  Poses are stored as a dict of bone -> (rotation_x,
    rotation_y, rotation_z) in degrees.
    """
    for pb in armature.pose.bones:
        pb.rotation_euler = (0, 0, 0)

    if pose_name == "idle":
        idle_rotations = {
            "UpperArm.L": (0, 0, -5),
            "UpperArm.R": (0, 0, 5),
            "ForeArm.L": (0, 0, -10),
            "ForeArm.R": (0, 0, 10),
            "Head": (0, 0, 2),
            "UpperLeg.L": (0, 0, 1),
            "UpperLeg.R": (0, 0, -1),
        }
        import math
        for bone_name, (rx, ry, rz) in idle_rotations.items():
            pb = armature.pose.bones.get(bone_name)
            if pb is not None:
                pb.rotation_euler = (
                    math.radians(rx), math.radians(ry), math.radians(rz)
                )


def parent_mesh_to_armature(
    mesh_obj: bpy.types.Object,
    armature: bpy.types.Object,
    subdivide: bool = True,
) -> None:
    """Parent *mesh_obj* to *armature* with automatic weights.

    A temporary Armature modifier is added so the mesh deforms with the
    skeleton.  When ``subdivide`` is True the mesh gets two subdivision
    levels first so automatic weight painting has enough geometry to
    work with.
    """
    if subdivide:
        _ensure_subsurf(mesh_obj, levels=2)

    # Select only the mesh then the armature (active) and parent.
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def _ensure_subsurf(obj: bpy.types.Object, levels: int = 2) -> None:
    """Add a Subdivision Surface modifier if one isn't already present."""
    if obj.modifiers.find("Subdivision") == -1:
        mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
        mod.levels = levels
        mod.render_levels = levels
