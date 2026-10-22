import numpy as np

from vision_engine.stages.confidence import evaluate_disease_prediction


def test_high_confidence_single_class_is_not_uncertain():
    result = evaluate_disease_prediction(["healthy"], np.array([0.92]))

    assert result["label"] == "healthy"
    assert result["confidence_rating"] == "high"
    assert result["is_uncertain"] is False
    assert result["is_near_tie"] is False


def test_low_confidence_prediction_is_marked_uncertain():
    result = evaluate_disease_prediction(
        ["healthy", "early_blight"], np.array([0.62, 0.38]), threshold=0.7
    )

    assert result["confidence_rating"] == "low"
    assert result["is_uncertain"] is True
    assert result["is_near_tie"] is False


def test_close_top_predictions_escalate_as_near_tie():
    result = evaluate_disease_prediction(
        ["early_blight", "late_blight"], np.array([0.61, 0.50])
    )

    assert result["confidence_rating"] == "near_tie"
    assert result["is_uncertain"] is True
    assert result["is_near_tie"] is True
    assert result["could_also_be"] == {
        "label": "late_blight",
        "confidence": 0.5,
        "margin": 0.11,
    }
