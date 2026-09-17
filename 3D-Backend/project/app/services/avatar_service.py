"""Avatar generation pipeline service.

Orchestrates the flow:

    Uploaded Image
        -> Image Validation
        -> Face Detection
        -> Feature Extraction
        -> Generate Avatar Parameters
        -> Return Avatar Configuration

Each step delegates to ``image_processor`` so the CV logic stays swappable.
"""

import logging

from app.services.image_processor import (
    detect_face,
    estimate_face_shape,
    estimate_skin_color,
    extract_face_features,
    validate_image,
)

logger = logging.getLogger(__name__)


def generate_avatar_config(image_bytes: bytes, name: str = "My Avatar") -> dict:
    """Run the full placeholder pipeline and return an avatar configuration dict.

    The returned dict is shaped to match ``AvatarCreate`` so a route can
    pass it straight into the avatars API once the user approves it.
    """
    logger.info("generate_avatar_config: starting pipeline for '%s'", name)

    # 1. Image validation
    if not validate_image(image_bytes):
        raise ValueError("Invalid or empty image provided")

    # 2. Face detection
    face = detect_face(image_bytes)
    if face is None:
        raise ValueError("No face detected in the uploaded image")

    # 3. Feature extraction
    features = extract_face_features(image_bytes, face)

    # 4. Derive avatar parameters
    skin_color = estimate_skin_color(image_bytes, face)
    face_shape = estimate_face_shape(features)

    # 5. Assemble the avatar configuration
    config = {
        "name": name,
        "skin_color": skin_color,
        "hair_style": "default",
        "hair_color": "#3B2A1A",
        "face_shape": face_shape,
        "body_type": "average",
        "model_url": None,
    }
    logger.info("generate_avatar_config: completed -> %s", config)
    return config
