from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.schemas import FeedbackRequest
from app.services import feedback as feedback_service


def test_create_farmer_feedback_validates_ownership():
    session = MagicMock()
    # Prediction exists but belongs to a different farmer
    prediction = SimpleNamespace(id=10, user_id="farmer-other")
    session.get.return_value = prediction

    req = FeedbackRequest(prediction_id=10, is_correct=True, farmer_note="Looks accurate")
    with pytest.raises(HTTPException) as exc_info:
        feedback_service.create_farmer_feedback(session, "farmer-me", req)
    assert exc_info.value.status_code == 403


def test_create_farmer_feedback_not_found():
    session = MagicMock()
    session.get.return_value = None

    req = FeedbackRequest(prediction_id=999, is_correct=False)
    with pytest.raises(HTTPException) as exc_info:
        feedback_service.create_farmer_feedback(session, "farmer-me", req)
    assert exc_info.value.status_code == 404


def test_create_farmer_feedback_success(monkeypatch):
    session = MagicMock()
    prediction = SimpleNamespace(id=10, user_id="farmer-me", disease="Early Blight", image=None)
    session.get.return_value = prediction
    saved_feedback = SimpleNamespace(id=42, prediction_id=10, is_correct=True, farmer_note="Good")

    add_fb_mock = MagicMock(return_value=saved_feedback)
    monkeypatch.setattr(feedback_service, "add_feedback", add_fb_mock)
    monkeypatch.setattr(feedback_service, "prediction_event", MagicMock())

    req = FeedbackRequest(prediction_id=10, is_correct=True, farmer_note="Good")
    res = feedback_service.create_farmer_feedback(session, "farmer-me", req)

    assert res.id == 42
    add_fb_mock.assert_called_once_with(
        session=session,
        prediction=prediction,
        is_correct=True,
        farmer_note="Good",
    )


def test_update_farmer_feedback_forbidden():
    session = MagicMock()
    fb = SimpleNamespace(id=5, prediction=SimpleNamespace(user_id="other-user"))
    session.get.return_value = fb

    req = FeedbackRequest(prediction_id=10, is_correct=False)
    with pytest.raises(HTTPException) as exc_info:
        feedback_service.update_farmer_feedback(session, "my-user", 5, req)
    assert exc_info.value.status_code == 403
