"""
Base avatar construction.

``create_base_avatar`` builds the full stylized humanoid mesh set:

    Head, Face, Eyes, Eyebrows, Nose, Mouth, Hair,
    Torso, Arms, Hands, Legs, Feet

Each body part is a separate low-poly mesh created with ``bpy.ops`` or
``bmesh`` primitives, then joined into a single ``Avatar_Body`` object so
shape keys and the armature modifier work on one unified mesh.

Shape keys are added at the end so ``change_face_shape`` and
``change_body_type`` can morph the mesh afterwards.
"""

from __future__ import annotations

import bpy
import bmesh
import math
from mathutils import Vector
from typing import Optional

from .config import AvatarConfig, BodyType, HairStyle
from .materials import create_material, _assign_material
from .armature import add_armature, parent_mesh_to_armature


# ---------------------------------------------------------------------------
# Primitive helpers
# ---------------------------------------------------------------------------

def _add_uv_sphere(name: str, location: tuple, radius: float, segments: int = 16, rings: int = 12) -> bpy.types.Object:
    """Create a UV sphere mesh and return the object."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, radius=radius, location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj


def _add_cylinder(name: str, location: tuple, radius: float, depth: float, rotation: tuple = (0, 0, 0), vertices: int = 12) -> bpy.types.Object:
    """Create a cylinder mesh and return the object."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj


def _add_cube(name: str, location: tuple, size: tuple, rotation: tuple = (0, 0, 0)) -> bpy.types.Object:
    """Create a scaled cube mesh and return the object."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    return obj


def _add_torus(name: str, location: tuple, major_radius: float, minor_radius: float, rotation: tuple = (0, 0, 0)) -> bpy.types.Object:
    """Create a torus mesh and return the object."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, minor_radius=minor_radius,
        location=location, rotation=rotation,
        major_segments=16, minor_segments=8,
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj


# ---------------------------------------------------------------------------
# Body-part builders
# ---------------------------------------------------------------------------

def _build_head(config: AvatarConfig) -> list[bpy.types.Object]:
    """Head sphere + neck."""
    head = _add_uv_sphere("Head", (0, 0, 1.52), 0.13, segments=24, rings=16)
    neck = _add_cylinder("Neck", (0, 0, 1.40), 0.045, 0.06, vertices=12)
    return [head, neck]


def _build_face(config: AvatarConfig) -> list[bpy.types.Object]:
    """Face plate (slightly flattened sphere on the front of the head)."""
    face = _add_uv_sphere("Face", (0, -0.02, 1.52), 0.12, segments=20, rings=14)
    # Flatten slightly on Y to suggest a face plane.
    face.scale = (1.0, 0.85, 1.05)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return [face]


def _build_eyes(config: AvatarConfig) -> list[bpy.types.Object]:
    """Two eyeball spheres plus iris discs."""
    eyes: list[bpy.types.Object] = []
    for side, x in (("L", 0.045), ("R", -0.045)):
        eyeball = _add_uv_sphere(f"EyeBall.{side}", (x, -0.11, 1.55), 0.025, segments=12, rings=8)
        # Slightly flatten the eyeball so it sits on the face.
        eyeball.scale.y = 0.6
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        eyes.append(eyeball)
    return eyes


def _build_eyebrows(config: AvatarConfig) -> list[bpy.types.Object]:
    """Two small flattened cylinders above the eyes."""
    brows: list[bpy.types.Object] = []
    for side, x in (("L", 0.045), ("R", -0.045)):
        brow = _add_cylinder(f"Eyebrow.{side}", (x, -0.115, 1.60), 0.018, 0.06,
                             rotation=(math.radians(90), 0, 0), vertices=8)
        brow.scale = (1.0, 1.0, 0.35)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        brows.append(brow)
    return brows


def _build_nose(config: AvatarConfig) -> list[bpy.types.Object]:
    """Small cone-ish sphere for the nose."""
    nose = _add_uv_sphere("Nose", (0, -0.135, 1.50), 0.018, segments=10, rings=6)
    nose.scale = (0.8, 1.2, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return [nose]


def _build_mouth(config: AvatarConfig) -> list[bpy.types.Object]:
    """Mouth as a flattened torus (smile arc)."""
    mouth = _add_torus("Mouth", (0, -0.115, 1.45), 0.035, 0.008,
                       rotation=(math.radians(90), 0, 0))
    mouth.scale = (1.0, 1.0, 0.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return [mouth]


def _build_hair(config: AvatarConfig) -> list[bpy.types.Object]:
    """Hair cap — a partial sphere sitting on top of the head.

    The style is controlled by ``config.hair_style`` and is morphed
    later by ``change_hair_style`` via a shape key, but we also build a
    base cap whose size depends on the style.
    """
    style_scale = {
        HairStyle.SHORT:  (1.05, 1.05, 1.10),
        HairStyle.MEDIUM: (1.08, 1.12, 1.20),
        HairStyle.LONG:   (1.10, 1.20, 1.35),
        HairStyle.BUZZ:   (1.02, 1.02, 1.04),
        HairStyle.BOB:    (1.12, 1.15, 1.18),
    }
    sx, sy, sz = style_scale.get(config.hair_style, style_scale[HairStyle.SHORT])

    hair = _add_uv_sphere("Hair", (0, 0.01, 1.55), 0.135, segments=20, rings=14)
    hair.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Trim the bottom half so it looks like a cap, not a full sphere.
    _delete_bottom_half(hair)
    return [hair]


def _delete_bottom_half(obj: bpy.types.Object) -> None:
    """Delete vertices below the object's local z = 0 plane."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    verts_to_delete = [v for v in bm.verts if v.co.z < -0.02]
    bmesh.ops.delete(bm, geom=verts_to_delete, context="VERTS")
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")


def _build_torso(config: AvatarConfig) -> list[bpy.types.Object]:
    """Torso as a tapered cube from chest to hips."""
    torso = _add_cube("Torso", (0, 0, 1.07), (0.22, 0.13, 0.30))
    return [torso]


def _build_arms(config: AvatarConfig) -> list[bpy.types.Object]:
    """Upper + forearms as cylinders on both sides."""
    arms: list[bpy.types.Object] = []
    for side, x in (("L", 0.28), ("R", -0.28)):
        upper = _add_cylinder(f"UpperArm.{side}", (x, 0, 1.25), 0.045, 0.26,
                              rotation=(0, math.radians(90), 0), vertices=12)
        fore = _add_cylinder(f"ForeArm.{side}", (x + 0.20, 0, 1.17), 0.038, 0.24,
                             rotation=(0, math.radians(90), 0), vertices=12)
        arms.extend([upper, fore])
    return arms


def _build_hands(config: AvatarConfig) -> list[bpy.types.Object]:
    """Simple sphere hands."""
    hands: list[bpy.types.Object] = []
    for side, x in (("L", 0.66), ("R", -0.66)):
        hand = _add_uv_sphere(f"Hand.{side}", (x, 0, 1.08), 0.04, segments=12, rings=8)
        hands.append(hand)
    return hands


def _build_legs(config: AvatarConfig) -> list[bpy.types.Object]:
    """Upper + lower legs as cylinders."""
    legs: list[bpy.types.Object] = []
    for side, x in (("L", 0.10), ("R", -0.10)):
        upper = _add_cylinder(f"UpperLeg.{side}", (x, 0, 0.69), 0.06, 0.40, vertices=12)
        lower = _add_cylinder(f"LowerLeg.{side}", (x, 0, 0.29), 0.05, 0.40, vertices=12)
        legs.extend([upper, lower])
    return legs


def _build_feet(config: AvatarConfig) -> list[bpy.types.Object]:
    """Feet as elongated cubes."""
    feet: list[bpy.types.Object] = []
    for side, x in (("L", 0.10), ("R", -0.10)):
        foot = _add_cube(f"Foot.{side}", (x, 0.06, 0.04), (0.07, 0.16, 0.05))
        feet.append(foot)
    return feet


# ---------------------------------------------------------------------------
# Shape keys
# ---------------------------------------------------------------------------

def _add_shape_key(obj: bpy.types.Object, name: str) -> bpy.types.ShapeKey:
    """Add (or get) a shape key on *obj* and return it."""
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    sk = obj.data.shape_keys.key_blocks.get(name)
    if sk is None:
        sk = obj.shape_key_add(name=name, from_mix=False)
    return sk


def _create_face_shape_keys(body: bpy.types.Object) -> None:
    """Create face-related shape keys: face_width, jaw_width, cheek_size, eye_size."""
    # Face width — scale x of head/face verts.
    sk = _add_shape_key(body, "face_width")
    _scale_verts_in_range(sk, z_range=(1.40, 1.65), axis="x", factor=1.15)

    sk = _add_shape_key(body, "jaw_width")
    _scale_verts_in_range(sk, z_range=(1.40, 1.48), axis="x", factor=1.20)

    sk = _add_shape_key(body, "cheek_size")
    _scale_verts_in_range(sk, z_range=(1.46, 1.54), axis="y", factor=1.15)

    sk = _add_shape_key(body, "eye_size")
    _scale_verts_in_range(sk, z_range=(1.53, 1.57), axis="all", factor=1.10)


def _create_body_shape_keys(body: bpy.types.Object) -> None:
    """Create body-proportion shape keys: body_slim, body_athletic."""
    sk = _add_shape_key(body, "body_slim")
    _scale_verts_in_range(sk, z_range=(0.80, 1.35), axis="x", factor=0.85)
    _scale_verts_in_range(sk, z_range=(0.80, 1.35), axis="y", factor=0.85)

    sk = _add_shape_key(body, "body_athletic")
    _scale_verts_in_range(sk, z_range=(0.80, 1.35), axis="x", factor=1.15)
    _scale_verts_in_range(sk, z_range=(0.80, 1.35), axis="y", factor=1.10)
    _scale_verts_in_range(sk, z_range=(0.25, 0.90), axis="x", factor=1.10)


def _scale_verts_in_range(
    shape_key: bpy.types.ShapeKey,
    z_range: tuple[float, float],
    axis: str,
    factor: float,
) -> None:
    """Populate *shape_key* data by scaling verts whose world z is in *z_range*.

    ``axis`` can be "x", "y", "all", or "z".
    """
    z_min, z_max = z_range
    for i, v in enumerate(shape_key.data):
        # shape_key.data is parallel to mesh vertices; use original vert z.
        orig_z = v.co.z  # already in local space (matches our build coords)
        if z_min <= orig_z <= z_max:
            if axis == "x" or axis == "all":
                v.co.x *= factor
            if axis == "y" or axis == "all":
                v.co.y *= factor
            if axis == "z" or axis == "all":
                v.co.z *= factor


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def create_base_avatar(config: AvatarConfig) -> bpy.types.Object:
    """Build the full base avatar and return the joined body object.

    Steps
    -----
    1. Clear the scene.
    2. Create all body-part meshes.
    3. Create materials (skin, hair, eyes).
    4. Join body parts into ``Avatar_Body``; keep Hair separate.
    5. Add shape keys.
    6. Create the armature and parent the body + hair to it.
    7. Apply initial body-type and face-shape morphs.
    """
    _clear_scene()

    # 1. Build meshes --------------------------------------------------
    parts: list[bpy.types.Object] = []
    parts += _build_head(config)
    parts += _build_face(config)
    parts += _build_eyes(config)
    parts += _build_eyebrows(config)
    parts += _build_nose(config)
    parts += _build_mouth(config)
    hair_parts = _build_hair(config)
    parts += _build_torso(config)
    parts += _build_arms(config)
    parts += _build_hands(config)
    parts += _build_legs(config)
    parts += _build_feet(config)

    # 2. Materials -----------------------------------------------------
    skin_mat = create_material("M_Skin", config.skin_color, roughness=0.50)
    hair_mat = create_material("M_Hair", config.hair_color, roughness=0.70)
    eye_mat = create_material("M_Eyes", config.eye_color, roughness=0.20)
    brow_mouth_mat = create_material("M_Brows", (0.15, 0.09, 0.05, 1.0), roughness=0.60)

    # 3. Assign materials to parts ------------------------------------
    skin_names = {"Head", "Neck", "Face", "Nose", "Torso",
                 "UpperArm.L", "ForeArm.L", "UpperArm.R", "ForeArm.R",
                 "Hand.L", "Hand.R", "UpperLeg.L", "LowerLeg.L",
                 "UpperLeg.R", "LowerLeg.R", "Foot.L", "Foot.R"}
    eye_names = {"EyeBall.L", "EyeBall.R"}
    brow_mouth_names = {"Eyebrow.L", "Eyebrow.R", "Mouth"}

    for obj in parts:
        if obj.name in skin_names:
            _assign_material(obj, skin_mat)
        elif obj.name in eye_names:
            _assign_material(obj, eye_mat)
        elif obj.name in brow_mouth_names:
            _assign_material(obj, brow_mouth_mat)
    for obj in hair_parts:
        _assign_material(obj, hair_mat)

    # 4. Join into Avatar_Body + Avatar_Hair ---------------------------
    body = _join_objects(parts, "Avatar_Body")
    hair = _join_objects(hair_parts, "Avatar_Hair")

    # 5. Shape keys ----------------------------------------------------
    _create_face_shape_keys(body)
    _create_body_shape_keys(body)

    # 6. Armature ------------------------------------------------------
    armature = add_armature("Armature")
    config.armature_name = armature.name
    parent_mesh_to_armature(body, armature, subdivide=True)
    parent_mesh_to_armature(hair, armature, subdivide=False)

    # 7. Initial morphs ------------------------------------------------
    _apply_body_type_keys(body, config.body_type)
    _apply_face_shape_keys(body, config.face_shape, config)

    return body


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def _clear_scene() -> None:
    """Delete every object, mesh, material, and armature in the file."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.cameras, bpy.data.lights):
        for item in list(coll):
            coll.remove(item)


def _join_objects(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    """Join *objects* into a single mesh object named *name*."""
    if not objects:
        raise ValueError("Cannot join an empty list of objects.")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = name
    return joined


def _apply_body_type_keys(body: bpy.types.Object, body_type: BodyType) -> None:
    """Set body shape-key values based on the BodyType preset."""
    ks = body.data.shape_keys
    if ks is None:
        return
    slim = ks.key_blocks.get("body_slim")
    athletic = ks.key_blocks.get("body_athletic")
    if body_type == BodyType.SLIM:
        if slim:
            slim.value = 1.0
        if athletic:
            athletic.value = 0.0
    elif body_type == BodyType.ATHLETIC:
        if slim:
            slim.value = 0.0
        if athletic:
            athletic.value = 1.0
    else:  # AVERAGE
        if slim:
            slim.value = 0.0
        if athletic:
            athletic.value = 0.0


def _apply_face_shape_keys(body: bpy.types.Object, face_shape, config: AvatarConfig) -> None:
    """Set face shape-key values based on the FaceShape preset + sliders."""
    ks = body.data.shape_keys
    if ks is None:
        return
    fw = ks.key_blocks.get("face_width")
    jw = ks.key_blocks.get("jaw_width")
    cs = ks.key_blocks.get("cheek_size")
    es = ks.key_blocks.get("eye_size")

    # Apply slider values first.
    if fw:
        fw.value = config.face_width
    if jw:
        jw.value = config.jaw_width
    if cs:
        cs.value = config.cheek_size
    if es:
        es.value = config.eye_size

    # Overlay preset defaults.
    presets = {
        "oval":   (0.50, 0.50, 0.50, 0.50),
        "round":  (0.75, 0.35, 0.80, 0.50),
        "square": (0.85, 0.85, 0.40, 0.50),
        "heart":  (0.40, 0.20, 0.60, 0.60),
    }
    vals = presets.get(face_shape.value if hasattr(face_shape, "value") else face_shape, presets["oval"])
    if fw:
        fw.value = max(fw.value, vals[0])
    if jw:
        jw.value = max(jw.value, vals[1])
    if cs:
        cs.value = max(cs.value, vals[2])
    if es:
        es.value = max(es.value, vals[3])
