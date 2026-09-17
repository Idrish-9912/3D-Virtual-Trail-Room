# Stylized 3D Avatar Generator

A modular Blender Python system for building customizable, stylized
Bitmoji-style 3D humanoid avatars, plus a React Three Fiber web viewer
for displaying the exported GLB.

## Project structure

```
.
├── blender/
│   ├── avatar_generator/         # Modular Python package
│   │   ├── __init__.py           # Public API
│   │   ├── config.py             # AvatarConfig dataclass + enums
│   │   ├── materials.py          # create_material, set_skin_color, set_hair_color
│   │   ├── base_avatar.py        # create_base_avatar + shape keys
│   │   ├── customization.py      # change_face_shape, change_body_type
│   │   ├── armature.py           # add_armature, parent_mesh_to_armature
│   │   ├── clothing.py           # apply_outfit (t-shirt, shirt, jacket, pants, shoes)
│   │   ├── poses.py              # apply_idle_pose, reset_pose
│   │   └── export.py             # export_avatar (GLB)
│   ├── run_avatar.py             # Entry point script
│   └── output/                   # Generated GLB files
├── src/                           # React Three Fiber viewer
│   ├── App.tsx
│   ├── main.tsx
│   ├── types.ts
│   └── components/
│       ├── AvatarModel.tsx       # GLB loader + placeholder
│       └── ControlPanel.tsx     # Customization UI
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Blender usage

### From the command line

```bash
blender --background --python blender/run_avatar.py -- --out blender/output/avatar.glb
```

### From the Blender Python console

```python
import sys
sys.path.insert(0, "blender")

from avatar_generator import (
    AvatarConfig, BodyType, HairStyle, FaceShape, OutfitType,
    create_base_avatar, set_skin_color, set_hair_color,
    apply_outfit, apply_idle_pose, export_avatar,
)

config = AvatarConfig(
    body_type=BodyType.ATHLETIC,
    hair_style=HairStyle.LONG,
    face_shape=FaceShape.ROUND,
    skin_color=(0.90, 0.70, 0.55, 1.0),
    hair_color=(0.10, 0.08, 0.05, 1.0),
    outfit_pieces=[OutfitType.JACKET, OutfitType.PANTS, OutfitType.SHOES],
    export_path="blender/output/avatar.glb",
)

create_base_avatar(config)
apply_outfit(config)
apply_idle_pose(config.armature_name)
export_avatar(config)
```

### Passing AI-generated parameters

`AvatarConfig` is a plain dataclass — any dict-like source (JSON from
an AI pipeline, a database row, etc.) can be mapped into it:

```python
import json
from avatar_generator import AvatarConfig

params = json.loads('{"body_type": "slim", "hair_style": "bob", "skin_color": [0.96, 0.78, 0.66, 1.0]}')
config = AvatarConfig(
    body_type=BodyType(params["body_type"]),
    hair_style=HairStyle(params["hair_style"]),
    skin_color=tuple(params["skin_color"]),
)
```

## Web viewer

```bash
npm install
npm run dev
```

The viewer loads `/avatar.glb` from the `public/` folder. To preview
your exported avatar, copy the GLB there:

```bash
mkdir -p public
cp blender/output/avatar.glb public/avatar.glb
```

If no GLB is found, a built-in placeholder avatar renders so you can
test the color and style controls immediately.

### Controls

- Drag to orbit, scroll to zoom
- Color pickers for skin, hair, shirt, pants, shoes
- Dropdowns for body type, hair style, and face shape

## Key design decisions

- **Single shared armature** — body, hair, and all clothing are
  parented to one humanoid rig with automatic weights, so clothing
  deforms with the avatar during animation.
- **Shape keys** — face width, jaw width, cheek size, eye size, and
  body proportions (slim / athletic) are morph targets on the body
  mesh, adjustable via `AvatarConfig` sliders or presets.
- **Separate clothing meshes** — each outfit piece is an independent
  object with its own material, making it easy to swap or hide pieces.
- **Web-optimized GLB** — Y-up, modifiers applied, no cameras/lights
  baked, no animation data (add later via Three.js).
