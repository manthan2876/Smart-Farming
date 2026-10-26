from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.services import expert as expert_service


def test_get_queue_items_formatting():
    session = MagicMock()
    now = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
    review = SimpleNamespace(
        id=1,
        prediction_id=101,
        status="pending",
        claimed_by=None,
        claimed_at=None,
        created_at=now,
        prediction=SimpleNamespace(
            crop="Tomato",
            disease="Early Blight",
            disease_conf=0.65,
            severity_pct=35.0,
            result={"crop": {"label": "Tomato"}, "disease": {"label": "Early Blight", "confidence": 0.65}},
        ),
    )
    session.scalars.return_value = [review]

    items = expert_service.get_queue_items(session)
    assert len(items) == 1
    assert items[0]["review_id"] == 1
    assert items[0]["crop"] == "Tomato"
    assert items[0]["disease"] == "Early Blight"
    assert items[0]["disease_conf"] == 0.65
    assert items[0]["status"] == "pending"


def test_claim_review_lease_not_found():
    session = MagicMock()
    session.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        expert_service.claim_review_lease(session, 999, "expert-1")
    assert exc_info.value.status_code == 404


def test_claim_review_lease_conflict():
    session = MagicMock()
    now = datetime.now(timezone.utc)
    review = SimpleNamespace(
        id=1,
        status="pending",
        claimed_by="expert-2",
        claimed_at=now - timedelta(minutes=5),  # Active claim
    )
    session.get.return_value = review

    with pytest.raises(HTTPException) as exc_info:
        expert_service.claim_review_lease(session, 1, "expert-1")
    assert exc_info.value.status_code == 409
    assert "currently claimed by another expert" in exc_info.value.detail


def test_release_review_lease():
    session = MagicMock()
    review = SimpleNamespace(
        id=1,
        claimed_by="expert-1",
        claimed_at=datetime.now(timezone.utc),
    )
    session.get.return_value = review

    res = expert_service.release_review_lease(session, 1, "expert-1")
    assert res["status"] == "released"
    assert review.claimed_by is None
    assert review.claimed_at is None
