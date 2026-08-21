"""
pipeline.py — Pipeline Orchestrator

THE ONLY job of this file is to call each service in the correct order.

NO AI logic lives here.
NO service calls another service directly.

Everything communicates through the shared context object.

Pipeline stages:

  1. OpenCV Preprocessing
  2. Crop Identification
  3. Decision Engine
  4. Disease Classification
  5. Severity Estimation
  6. Pest Classification

Current pest model:
    YOLOv8 Classification

IMPORTANT:
    The current pest model performs IMAGE CLASSIFICATION, not object detection.
    Therefore it predicts pest classes from the complete processed leaf image.
"""

from pathlib import Path
from typing import Any

import yaml

# ============================================================================
# SERVICE IMPORTS
# ============================================================================

from services.preprocessing.service import OpenCVPreprocessorService
from services.crop_identifier.predictor import predict_crop
from services.decision_engine.router import route_to_disease_model
from services.disease_classifier.predictor import predict_disease
from services.severity.estimator import estimate_severity
from services.pest_detector.predictor import predict_pest


# ============================================================================
# CONFIGURATION
# ============================================================================

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load_config(config_path: Path = _CONFIG_PATH) -> dict[str, Any]:
    """
    Load config.yaml.

    Returns:
        Parsed configuration dictionary.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_CONFIG: dict[str, Any] = _load_config()


# ============================================================================
# PREPROCESSOR
# ============================================================================

_PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)


# ============================================================================
# PIPELINE
# ============================================================================

def run_pipeline(context: dict) -> dict:
    """
    Run the complete Smart Farming AI pipeline.

    Execution order:

        preprocessing
            ↓
        crop identification
            ↓
        decision routing
            ↓
        disease classification
            ↓
        severity estimation
            ↓
        pest classification

    Each service:
        - reads from context
        - writes to context
        - updates its own status

    Args:
        context:
            Context created using create_context().

    Returns:
        Fully populated pipeline context.
    """

    # ========================================================================
    # STAGE 1 — PREPROCESSING
    # ========================================================================

    context = _PREPROCESSOR.process(context)

    # If preprocessing failed, there is no valid image for the models.
    if context["status"]["preprocessing"] != "completed":
        return context

    # ========================================================================
    # STAGE 2 — CROP IDENTIFICATION
    # ========================================================================

    context = predict_crop(
        context,
        _CONFIG,
    )

    # ========================================================================
    # STAGE 3 — DECISION ENGINE
    # ========================================================================
    #
    # Crop prediction determines which disease model should be used.
    #
    # Example:
    #
    #     Cotton
    #        ↓
    #     disease_Cotton.pth
    #
    # ========================================================================

    context = route_to_disease_model(
        context,
        _CONFIG,
    )

    # ========================================================================
    # STAGE 4 — DISEASE CLASSIFICATION
    # ========================================================================

    context = predict_disease(
        context,
        _CONFIG,
    )

    # ========================================================================
    # STAGE 5 — SEVERITY ESTIMATION
    # ========================================================================

    context = estimate_severity(
        context,
    )

    # ========================================================================
    # STAGE 6 — PEST CLASSIFICATION
    # ========================================================================
    #
    # IMPORTANT:
    #
    # The current YOLO model is a classification model.
    #
    # It predicts:
    #
    #     "Leaf Miner: 92.3%"
    #
    # It does NOT provide:
    #
    #     bounding boxes
    #     number of pests
    #     pest coordinates
    #     individual pest instances
    #
    # ========================================================================

    context = predict_pest(
        context,
        _CONFIG,
    )

    return context


# ============================================================================
# CONFIG RELOAD
# ============================================================================

def reload_config() -> None:
    """
    Reload config.yaml from disk.

    Useful when model paths or thresholds are changed without restarting
    the application.
    """

    global _CONFIG, _PREPROCESSOR

    _CONFIG = _load_config()
    _PREPROCESSOR = OpenCVPreprocessorService(_CONFIG)

    print(
        "[Pipeline] Config reloaded from",
        _CONFIG_PATH,
    )