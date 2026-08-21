"""
context.py — Factory for the shared pipeline context object.

Every stage in the pipeline reads from and writes to this same dict.
This is the single most important architectural decision in the project:
no stage calls another stage directly — they all communicate via the context.
"""

import uuid
from typing import Any


def create_context(
    image_path: str,
    user_id: str = "anon",
    location: str = "Unknown",
    language: str = "English",
) -> dict[str, Any]:
    """
    Create a fresh pipeline context for a single prediction request.

    Args:
        image_path: Absolute or relative path to the raw uploaded image.
        user_id: Identifier for the requesting user.
        location: Geographic location of the farmer.
        language: Preferred output language.

    Returns:
        A context dict with all fields initialised to their pending / None state.
    """

    return {
        "request_id": str(uuid.uuid4()),

        # ====================================================================
        # USER / REQUEST INFORMATION
        # ====================================================================

        "user": {
            "user_id": user_id,
            "location": location,
            "language": language,
        },

        # ====================================================================
        # IMAGE INFORMATION
        # ====================================================================

        "image": {
            # Original uploaded image
            "raw_path": str(image_path),

            # Processed image saved by preprocessing
            "processed_path": None,

            # In-memory processed leaf image (BGR)
            "leaf_crop": None,

            # Image quality metrics
            "quality_score": None,
            "blur_score": None,
            "brightness_score": None,
            "leaf_detected": False,
        },

        # ====================================================================
        # CROP IDENTIFICATION
        # ====================================================================

        "crop": {
            "label": None,
            "confidence": None,
        },

        # ====================================================================
        # DISEASE CLASSIFICATION
        # ====================================================================

        "disease": {
            "label": None,
            "confidence": None,
            "model_used": None,
            "all_probs": None,
        },

        # ====================================================================
        # SEVERITY ESTIMATION
        # ====================================================================

        "severity": {
            "percent": None,
            "affected_area": None,
            "bucket": None,
        },

        # ====================================================================
        # PEST CLASSIFICATION
        # ====================================================================
        #
        # IMPORTANT:
        # The current YOLO model is a CLASSIFICATION model.
        #
        # It predicts which pest class is present in the image.
        # It does NOT detect individual pest objects or provide bounding boxes.
        #
        # Example:
        #
        # pests = [
        #     {
        #         "label": "Leaf Miner",
        #         "confidence": 0.923
        #     },
        #     ...
        # ]
        #
        # ====================================================================

        "pests": [],

        "pest_classification": {
            "model_type": "classification",
            "model_used": None,
            "top_k": 3,
            "all_probs": None,
        },

        # ====================================================================
        # WEATHER
        # ====================================================================

        "weather": {},

        # ====================================================================
        # RECOMMENDATION
        # ====================================================================

        "recommendation": {},

        # ====================================================================
        # NOTES / WARNINGS
        # ====================================================================

        "notes": [],

        # ====================================================================
        # PIPELINE STATUS
        # ====================================================================

        "status": {
            "preprocessing": "pending",
            "crop_identification": "pending",
            "decision_routing": "pending",
            "disease_classification": "pending",
            "severity": "pending",

            # Keep the existing public pipeline status name for compatibility.
            "pest_detection": "pending",

            "recommendation": "pending",
        },
    }