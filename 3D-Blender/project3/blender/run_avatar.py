"""
Entry point for the Blender avatar generator.

Run from inside Blender (headless or GUI):

    blender --background --python run_avatar.py

Or from the system command line with Blender's Python:

    blender --background --python run_avatar.py -- --out blender/output/avatar.glb

The script builds a full avatar from an ``AvatarConfig``, applies an
outfit, sets an idle pose, and exports a web-ready GLB.
"""

from __future__ import annotations

import sys
import bpy

# Make sure the package is importable when run as a loose script.
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

from avatar_generator import (
    AvatarConfig,
    BodyType,
    HairStyle,
    FaceShape,
    OutfitType,
    create_base_avatar,
    set_skin_color,
    set_hair_color,
    apply_outfit,
    apply_idle_pose,
    export_avatar,
)


def build_default_avatar(export_path: str = "blender/output/avatar.glb") -> str:
    """Build a full avatar with the default config and export it."""
    config = AvatarConfig(
        name="DefaultAvatar",
        body_type=BodyType.AVERAGE,
        hair_style=HairStyle.SHORT,
        face_shape=FaceShape.OVAL,
        outfit_pieces=[OutfitType.TSHIRT, OutfitType.PANTS, OutfitType.SHOES],
        export_path=export_path,
    )

    # 1. Build the base avatar (head, face, eyes, hair, torso, limbs).
    create_base_avatar(config)

    # 2. Customize colors (optional — defaults are already applied).
    # set_skin_color(config, (0.90, 0.70, 0.55, 1.0))
    # set_hair_color(config, (0.10, 0.08, 0.05, 1.0))

    # 3. Add clothing.
    apply_outfit(config)

    # 4. Pose.
    apply_idle_pose(config.armature_name or "Armature")

    # 5. Export to GLB.
    return export_avatar(config)


def main() -> None:
    """Parse simple CLI args and run ``build_default_avatar``."""
    export_path = "blender/output/avatar.glb"
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        for i, arg in enumerate(args):
            if arg == "--out" and i + 1 < len(args):
                export_path = args[i + 1]

    path = build_default_avatar(export_path)
    print(f"Avatar exported to: {path}")


if __name__ == "__main__":
    main()
