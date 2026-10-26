from __future__ import annotations

import os
import sys
from pathlib import Path
import pytest
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# Ensure backend/src comes first so "app" resolves to backend app, not ai_service/app.py
if str(ROOT_DIR / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend" / "src"))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "ai_service") not in sys.path:
    sys.path.append(str(ROOT_DIR / "ai_service"))

from ai_service.vision_engine.loader import load_yolo
from ai_service.vision_engine.stages.pest_detector import predict_pest


def test_pest_model_weights_exist():
    """Verify that pest_classifier.pt exists on disk and is a valid binary."""
    model_path = ROOT_DIR / "ai_service" / "models" / "pest_classifier" / "pest_classifier.pt"
    assert model_path.exists(), f"Model file missing at: {model_path}"
    assert model_path.stat().st_size > 1024 * 1024, "Model file is an LFS pointer or too small!"


def test_pest_model_loading_and_architecture():
    """Verify YOLO model loads and exposes correct classification taxonomy."""
    model_path = ROOT_DIR / "ai_service" / "models" / "pest_classifier" / "pest_classifier.pt"
    model = load_yolo(str(model_path))
    assert model is not None, "Failed to load YOLO pest model."
    assert getattr(model, "task", None) == "classify", f"Expected 'classify' task, got {model.task}"
    names = getattr(model, "names", {})
    expected_classes = {"Aphid", "Army Worm", "Leaf Miner", "Spider Mite"}
    assert set(names.values()) == expected_classes, f"Class mismatch: {names.values()}"


def test_pest_prediction_pipeline_contract():
    """Test full predict_pest stage contract with clean foliage (no pests)."""
    model_path = "models/pest_classifier/pest_classifier.pt"
    test_img = np.full((224, 224, 3), 128, dtype=np.uint8)

    context = {
        "status": {"preprocessing": "completed"},
        "image": {"leaf_crop": test_img},
        "pests": [],
    }
    config = {
        "models": {
            "pest_classifier": {
                "path": model_path
            }
        },
        "thresholds": {
            "pest_confidence": 0.65
        },
        "device": "cpu"
    }

    result = predict_pest(context, config)
    assert result["status"]["pest_detection"] == "completed"
    pest_block = result.get("pest_classification", {})
    assert pest_block.get("available") is True
    assert "top_predictions" in pest_block
    assert len(pest_block["top_predictions"]) > 0


def test_pest_classifier_accuracy_on_test_subset():
    """Verify inference on real held-out pest test images."""
    import glob
    import cv2
    from ultralytics import YOLO

    model_path = str(ROOT_DIR / "ai_service" / "models" / "pest_classifier" / "pest_classifier.pt")
    model = YOLO(model_path)

    classes = ["Aphid", "Army Worm", "Leaf Miner", "Spider Mite"]
    total = 0
    correct = 0

    for cls in classes:
        imgs = glob.glob(str(ROOT_DIR / f"Datasets/pest_dataset/test/{cls}/*.*"))[:5]
        for p in imgs:
            img = cv2.imread(p)
            if img is None:
                continue
            res = model.predict(source=img, verbose=False, device="cpu")
            pred_name = res[0].names[res[0].probs.top1]
            total += 1
            if pred_name == cls:
                correct += 1

    assert total > 0, "No test images found in Datasets/pest_dataset/test"
    acc = correct / total
    assert acc >= 0.85, f"Pest classification accuracy too low on sample: {acc:.2%}"
