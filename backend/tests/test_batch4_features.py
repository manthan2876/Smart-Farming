"""
test_batch4_features.py — Batch 4 Integration & Calibration Tests
Tests confidence calibration (temperature scaling, ECE, Brier score),
model pipeline calibration integration, and Model Card evidence specifications.
"""

from pathlib import Path
import pytest
import numpy as np
import yaml

from app.core.calibration import (
    apply_temperature_scaling,
    calibrate_probability_scalar,
    compute_ece,
)


# ── 1. Calibration Mathematics & Algorithms ────────────────────────────────────

def test_temperature_scaling_identity():
    """At T=1.0, temperature-scaled softmax matches standard softmax."""
    logits = np.array([[2.0, 1.0, 0.1]])
    probs_t1 = apply_temperature_scaling(logits, temperature=1.0)
    
    # Standard softmax
    exp_l = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    expected = exp_l / np.sum(exp_l, axis=-1, keepdims=True)
    
    np.testing.assert_allclose(probs_t1, expected, rtol=1e-5)
    assert np.isclose(np.sum(probs_t1), 1.0)


def test_temperature_scaling_softens_probabilities_and_preserves_rank():
    """T > 1.0 softens overconfidence while strictly preserving label rank ordering."""
    logits = np.array([[5.0, 2.0, 0.0]])
    raw_probs = apply_temperature_scaling(logits, temperature=1.0)
    scaled_probs = apply_temperature_scaling(logits, temperature=1.5)
    
    # Peak probability should decrease (less overconfident)
    assert scaled_probs[0, 0] < raw_probs[0, 0]
    # Minor classes receive slightly higher probability
    assert scaled_probs[0, 1] > raw_probs[0, 1]
    assert scaled_probs[0, 2] > raw_probs[0, 2]
    # Rank ordering remains unchanged
    assert np.argmax(scaled_probs) == np.argmax(raw_probs)
    assert np.argsort(scaled_probs)[0].tolist() == np.argsort(raw_probs)[0].tolist()
    assert np.isclose(np.sum(scaled_probs), 1.0)


def test_temperature_scaling_invalid_temperature():
    """T <= 0 raises ValueError."""
    logits = np.array([[1.0, 2.0]])
    with pytest.raises(ValueError):
        apply_temperature_scaling(logits, temperature=0.0)
    with pytest.raises(ValueError):
        apply_temperature_scaling(logits, temperature=-1.2)


def test_calibrate_probability_scalar():
    """Validates scalar probability calibration across classes."""
    # Identity at T=1.0
    assert np.isclose(calibrate_probability_scalar(0.95, temperature=1.0), 0.95)
    
    # When T > 1.0, overconfident 0.95 is calibrated downwards
    calibrated = calibrate_probability_scalar(0.95, temperature=1.15, num_classes=5)
    assert calibrated < 0.95
    assert calibrated > 0.50


def test_compute_ece_perfect_calibration():
    """A model whose confidence exactly equals its accuracy yields ECE ~ 0."""
    # 100 samples with 80% confidence, exactly 80 are correct
    n_samples = 100
    y_true = np.array([0] * 80 + [1] * 20)
    # Predicted probabilities: 80% for class 0, 20% for class 1
    y_probs = np.array([[0.8, 0.2]] * 100)
    
    result = compute_ece(y_true, y_probs, num_bins=10)
    assert "ece" in result
    assert "mce" in result
    assert "brier_score" in result
    assert result["num_samples"] == 100
    # Expected Calibration Error for the bin containing 0.8 is 0 because accuracy == confidence == 0.8
    assert result["ece"] == 0.0


def test_compute_ece_overconfident_model():
    """A model reporting 99% confidence but only 50% accuracy produces significant ECE."""
    n_samples = 100
    y_true = np.array([0] * 50 + [1] * 50)
    # Model predicts class 0 with 0.99 confidence for all samples
    y_probs = np.array([[0.99, 0.01]] * 100)
    
    result = compute_ece(y_true, y_probs, num_bins=10)
    # ECE should be approximately |0.50 - 0.99| = 0.49
    assert result["ece"] > 0.45
    assert result["mce"] > 0.45
    assert result["brier_score"] > 0.20


def test_compute_ece_empty_input():
    """Empty inputs return graceful zeroed stats."""
    result = compute_ece([], np.empty((0, 3)), num_bins=10)
    assert result["ece"] == 0.0
    assert result["num_samples"] == 0
    assert result["bins"] == []


# ── 2. Config Calibration Integration ─────────────────────────────────────────

def test_yaml_config_contains_temperature_calibration():
    """Verifies backend and model_service config.yaml specify calibrated temperatures."""
    backend_config = Path("backend/config.yaml")
    assert backend_config.exists()
    
    with open(backend_config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    models = cfg.get("models", {})
    # Crop identifier calibration
    crop_cfg = models.get("crop_identifier", {})
    assert "temperature" in crop_cfg
    assert crop_cfg["temperature"] > 1.0
    
    # Disease models calibration
    disease_models = models.get("disease_models", {})
    for crop in ["Cotton", "Groundnut", "Pepper_Bell", "Potato", "Tomato"]:
        assert crop in disease_models
        d_cfg = disease_models[crop]
        assert "temperature" in d_cfg
        assert 1.0 < d_cfg["temperature"] <= 1.3


# ── 3. Model Cards Documentation Evidence Verification ────────────────────────

def test_model_cards_contain_per_class_metrics_and_field_sets():
    """Validates that Docs/Model_Cards.md contains per-class metrics and field-set scores."""
    model_cards_path = Path("Docs/Model_Cards.md")
    assert model_cards_path.exists()
    
    content = model_cards_path.read_text(encoding="utf-8")
    
    # 1. Crop Identifier Evidence
    assert "Per-Class Metrics (Held-Out Test Set, N = 4,260)" in content
    assert "In-Situ Field Set vs. Controlled Environment Breakdown" in content
    assert "Uncontrolled Environment (Field)" in content
    assert "99.35%" in content
    assert "Expected Calibration Error (ECE)" in content
    
    # 2. Disease Classifiers Evidence
    for crop_name in ["Cotton", "Groundnut", "Pepper Bell", "Potato", "Tomato"]:
        assert f"### 2" in content
        assert crop_name in content
        assert "Per-Class Metrics" in content
        assert "Confidence Calibration" in content
    
    # Specific per-class validation checks
    assert "Alternaria Leaf Spot" in content
    assert "Bacterial Blight" in content
    assert "Early Leaf Spot" in content or "Leaf Spot" in content
    assert "Early Blight" in content
    assert "Late Blight" in content
    
    # 3. Pest Classifier Evidence
    assert "3. Pest Classifier" in content
    assert "Aphid" in content
    assert "Army Worm" in content
    assert "Leaf Miner" in content
    assert "Spider Mite" in content
    assert "In-Situ Field Leaf Damage Set" in content


# ── 4. Pipeline Stage Temperature Scaling Integration Tests ───────────────────

def test_predict_crop_with_temperature_scaling():
    """Verify crop_identifier stage scales logits and tags calibrated metadata."""
    import sys
    from unittest.mock import MagicMock, patch
    import torch

    sys.path.insert(0, str(Path("model_service").resolve()))
    from src.stages.crop_identifier import predict_crop

    mock_model = MagicMock()
    mock_model.return_value = torch.tensor([[5.0, 1.0, 0.5, 0.2, 0.1]])
    classes = ["Cotton", "Groundnut", "Pepper_Bell", "Potato", "Tomato"]

    context = {
        "status": {"preprocessing": "completed"},
        "image": {"leaf_crop": np.zeros((224, 224, 3), dtype=np.uint8)},
        "crop": {},
    }
    config = {
        "models": {
            "crop_identifier": {
                "path": "dummy.pth",
                "labels": "dummy.json",
                "temperature": 1.08,
            }
        },
        "thresholds": {"crop_confidence": 0.7},
    }

    with patch("src.stages.crop_identifier.load_efficientnet", return_value=(mock_model, classes)):
        res = predict_crop(context, config)

    assert res["status"]["crop_identification"] == "completed"
    assert res["crop"]["label"] == "Cotton"
    assert res["crop"]["is_calibrated"] is True
    assert res["crop"]["temperature"] == 1.08
    assert 0.0 < res["crop"]["confidence"] <= 1.0


def test_predict_disease_with_temperature_scaling():
    """Verify disease_classifier stage applies temperature scaling and tags calibrated metadata."""
    import sys
    from unittest.mock import MagicMock, patch
    import torch

    sys.path.insert(0, str(Path("model_service").resolve()))
    from src.stages.disease_classifier import predict_disease

    mock_model = MagicMock()
    mock_model.return_value = torch.tensor([[4.0, 1.0, 0.2, 0.1]])
    classes = ["Alternaria Leaf Spot", "Bacterial Blight", "Fusarium Wilt", "Healthy"]

    context = {
        "status": {"decision_routing": "completed"},
        "image": {"leaf_crop": np.zeros((224, 224, 3), dtype=np.uint8)},
        "disease": {},
        "_disease_model_cfg": {
            "path": "dummy_disease.pth",
            "labels": "dummy_labels.json",
            "arch": "efficientnet_b2",
            "temperature": 1.12,
        },
    }
    config = {
        "thresholds": {"disease_confidence": 0.7, "near_tie_margin": 0.15},
    }

    with patch("src.stages.disease_classifier.load_efficientnet", return_value=(mock_model, classes)):
        res = predict_disease(context, config)

    assert res["status"]["disease_classification"] == "completed"
    assert res["disease"]["label"] == "Alternaria Leaf Spot"
    assert res["disease"]["is_calibrated"] is True
    assert res["disease"]["temperature"] == 1.12
    assert 0.0 < res["disease"]["confidence"] <= 1.0

