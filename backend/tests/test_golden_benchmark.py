from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repository root, ai_service, and backend/src are available on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "ai_service") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "ai_service"))
if str(ROOT_DIR / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend" / "src"))

import pytest
import numpy as np
from ai_service.vision_engine.stages.decision_router import route_to_disease_model
from ai_service.vision_engine.stages.severity import _severity_bucket
from ai_service.routers.advisory import validate_advisory_safety, BANNED_AGROCHEMICALS

# 30-image golden benchmark manifest (6 per crop: 4 diseased, 2 healthy)
GOLDEN_BENCHMARK = [
    # Cotton (6)
    {"id": "cot_01", "crop": "Cotton", "condition": "Bacterial Blight", "expected_status": "supported_crop"},
    {"id": "cot_02", "crop": "Cotton", "condition": "Alternaria Leaf Spot", "expected_status": "supported_crop"},
    {"id": "cot_03", "crop": "Cotton", "condition": "Curl Virus", "expected_status": "supported_crop"},
    {"id": "cot_04", "crop": "Cotton", "condition": "Fusarium Wilt", "expected_status": "supported_crop"},
    {"id": "cot_05", "crop": "Cotton", "condition": "Healthy", "expected_status": "supported_crop"},
    {"id": "cot_06", "crop": "Cotton", "condition": "Healthy", "expected_status": "supported_crop"},

    # Groundnut (6)
    {"id": "gnd_01", "crop": "Groundnut", "condition": "Early Leaf Spot", "expected_status": "supported_crop"},
    {"id": "gnd_02", "crop": "Groundnut", "condition": "Late Leaf Spot", "expected_status": "supported_crop"},
    {"id": "gnd_03", "crop": "Groundnut", "condition": "Rust", "expected_status": "supported_crop"},
    {"id": "gnd_04", "crop": "Groundnut", "condition": "Rosette", "expected_status": "supported_crop"},
    {"id": "gnd_05", "crop": "Groundnut", "condition": "Healthy", "expected_status": "supported_crop"},
    {"id": "gnd_06", "crop": "Groundnut", "condition": "Healthy", "expected_status": "supported_crop"},

    # Pepper Bell (6)
    {"id": "pep_01", "crop": "Pepper Bell", "condition": "Bacterial Spot", "expected_status": "supported_crop"},
    {"id": "pep_02", "crop": "Pepper Bell", "condition": "Cercospora Leaf Spot", "expected_status": "supported_crop"},
    {"id": "pep_03", "crop": "Pepper Bell", "condition": "Edema", "expected_status": "supported_crop"},
    {"id": "pep_04", "crop": "Pepper Bell", "condition": "Powdery Mildew", "expected_status": "supported_crop"},
    {"id": "pep_05", "crop": "Pepper Bell", "condition": "Healthy", "expected_status": "supported_crop"},
    {"id": "pep_06", "crop": "Pepper Bell", "condition": "Healthy", "expected_status": "supported_crop"},

    # Potato (6)
    {"id": "pot_01", "crop": "Potato", "condition": "Early Blight", "expected_status": "supported_crop"},
    {"id": "pot_02", "crop": "Potato", "condition": "Late Blight", "expected_status": "supported_crop"},
    {"id": "pot_03", "crop": "Potato", "condition": "Nematode", "expected_status": "supported_crop"},
    {"id": "pot_04", "crop": "Potato", "condition": "Virus", "expected_status": "supported_crop"},
    {"id": "pot_05", "crop": "Potato", "condition": "Healthy", "expected_status": "supported_crop"},
    {"id": "pot_06", "crop": "Potato", "condition": "Healthy", "expected_status": "supported_crop"},

    # Tomato (6)
    {"id": "tom_01", "crop": "Tomato", "condition": "Bacterial Spot", "expected_status": "supported_crop"},
    {"id": "tom_02", "crop": "Tomato", "condition": "Early Blight", "expected_status": "supported_crop"},
    {"id": "tom_03", "crop": "Tomato", "condition": "Late Blight", "expected_status": "supported_crop"},
    {"id": "tom_04", "crop": "Tomato", "condition": "Yellow Curl Virus", "expected_status": "supported_crop"},
    {"id": "tom_05", "crop": "Tomato", "condition": "Healthy", "expected_status": "supported_crop"},
    {"id": "tom_06", "crop": "Tomato", "condition": "Healthy", "expected_status": "supported_crop"},
]


def test_golden_benchmark_structure():
    """Verify golden regression suite contains 30 items, 6 per crop."""
    assert len(GOLDEN_BENCHMARK) == 30
    from collections import Counter
    counts = Counter(b["crop"] for b in GOLDEN_BENCHMARK)
    assert counts["Cotton"] == 6
    assert counts["Groundnut"] == 6
    assert counts["Pepper Bell"] == 6
    assert counts["Potato"] == 6
    assert counts["Tomato"] == 6


def test_canonical_severity_scale():
    """Verify canonical severity mapping matches Healthy / Mild / Moderate / Severe."""
    assert _severity_bucket(0.0) == "Healthy"
    assert _severity_bucket(12.5) == "Mild"
    assert _severity_bucket(35.0) == "Moderate"
    assert _severity_bucket(68.0) == "Severe"


def test_advisory_banned_pesticide_blocking():
    """Agronomic guardrail must block prohibited chemicals (e.g. Monocrotophos, Endosulfan)."""
    kb_entry = {
        "chemical_options": [{"chemical": "Mancozeb 75 WP", "dosage": "2 g/L"}],
        "organic_options": [{"treatment": "Neem oil 5ml/L"}],
    }

    # Banned agrochemical should be rejected immediately
    for banned in ["monocrotophos", "endosulfan", "paraquat", "chlorpyrifos", "phorate"]:
        malicious_output = {
            "immediate_action": f"Apply {banned} immediately at 5ml/L.",
            "treatment": "Follow label directions.",
            "prevention": "Spray weekly.",
            "monitoring": "Check foliage.",
        }
        is_safe, reason = validate_advisory_safety(malicious_output, kb_entry)
        assert is_safe is False
        assert banned in reason.lower()

    # Approved recommendation should pass
    clean_output = {
        "immediate_action": "Isolate affected plants.",
        "treatment": "Spray Mancozeb 75 WP at 2 g/L water.",
        "prevention": "Ensure good spacing and air circulation.",
        "monitoring": "Inspect weekly for new spots.",
    }
    is_safe, _ = validate_advisory_safety(clean_output, kb_entry)
    assert is_safe is True


def test_uncertain_crop_dual_run_conflict_escalation():
    """When crop identification confidence is in the uncertain band (0.50-0.75), conflicting disease diagnoses must escalate."""
    context = {
        "status": {
            "crop_identification": "completed",
            "decision_routing": "pending",
        },
        "crop": {
            "label": "Tomato",
            "confidence": 0.58,
            "is_uncertain_band": True,
            "top2": [
                {"label": "Tomato", "confidence": 0.58},
                {"label": "Potato", "confidence": 0.38},
            ],
        },
        "disease": {},
        "notes": [],
    }

    config = {
        "thresholds": {"crop_confidence": 0.70},
        "models": {
            "disease_models": {
                "Tomato": {"path": "models/disease_Tomato.pth", "labels": "models/labels_Tomato.json"},
                "Potato": {"path": "models/disease_Potato.pth", "labels": "models/labels_Potato.json"},
            }
        },
    }

    routed = route_to_disease_model(context, config)
    assert routed["status"]["decision_routing"] == "completed_uncertain_dual_run"
    assert len(routed["_dual_run_crops"]) == 2


def test_out_of_distribution_leaf_rejection():
    """Non-crop leaf or noisy image with high entropy / low confidence must be rejected as OOD."""
    context = {
        "status": {
            "crop_identification": "completed",
            "decision_routing": "pending",
        },
        "crop": {
            "label": "Tomato",
            "confidence": 0.32,  # Low confidence OOD
            "status": "out_of_distribution",
            "is_uncertain": True,
        },
        "disease": {},
        "notes": [],
    }

    config = {
        "thresholds": {"crop_confidence": 0.70},
        "models": {
            "disease_models": {
                "Tomato": {"path": "models/disease_Tomato.pth", "labels": "models/labels_Tomato.json"}
            }
        },
    }

    routed = route_to_disease_model(context, config)
    assert routed["status"]["decision_routing"] == "out_of_distribution"
    assert routed["disease"]["requires_expert_review"] is True
    assert routed["disease"]["escalation_reason"] == "out_of_distribution"
    assert "Unrecognized" in routed["disease"]["label"]
