from app.schemas.prediction import PredictionResponse


def test_prediction_response_accepts_normalized_history_and_legacy_fields() -> None:
    response = PredictionResponse.model_validate(
        {
            "prediction_id": 12,
            "created_at": "2026-10-22T12:00:00+00:00",
            "crop": {"label": "Cotton", "confidence": 0.98},
            "status": {"pipeline": "completed", "expert_review": "verified"},
            "historical_images": [
                {
                    "id": 7,
                    "created_at": "2026-10-20T12:00:00+00:00",
                    "disease": "Leaf blight",
                    "severity_pct": 37.5,
                    "severity_bucket": "Moderate",
                    "raw_url": "https://example.invalid/signed-image",
                }
            ],
            "legacy_result_field": {"preserved": True},
        }
    )

    assert response.prediction_id == 12
    assert response.crop is not None and response.crop.label == "Cotton"
    assert response.status is not None and response.status.pipeline == "completed"
    assert response.historical_images is not None
    assert response.historical_images[0].severity_pct == 37.5
    assert response.model_extra == {"legacy_result_field": {"preserved": True}}
