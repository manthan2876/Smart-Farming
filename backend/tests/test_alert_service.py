from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.crud.alerts import mark_user_alert_read
from app.services import alerts as alert_service


def test_list_alerts_serializes_and_localizes_results(monkeypatch):
    created_at = datetime(2026, 10, 22, tzinfo=timezone.utc)
    alert = SimpleNamespace(
        id=7,
        prediction_id=12,
        kind="weather",
        severity="high",
        title="Heavy rain",
        body="Check the field.",
        is_read=False,
        created_at=created_at,
    )
    session = MagicMock()
    query = session.query.return_value
    query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [alert]
    session.get.return_value = SimpleNamespace(language="Gujarati")
    overlay = MagicMock()
    monkeypatch.setattr(alert_service, "overlay_entity_translations", overlay)

    result = alert_service.list_alerts(session, "user-1", 5, 150, None)

    assert result == [{
        "id": 7,
        "prediction_id": 12,
        "kind": "weather",
        "severity": "high",
        "title": "Heavy rain",
        "body": "Check the field.",
        "is_read": False,
        "created_at": created_at.isoformat(),
    }]
    query.filter.return_value.order_by.return_value.offset.assert_called_once_with(5)
    query.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_once_with(100)
    overlay.assert_called_once()
    overlay_call = overlay.call_args
    assert overlay_call.args[:3] == (session, result, "alert")
    assert overlay_call.args[3](result[0]) == 7
    assert overlay_call.args[4:] == (["title", "body"], "Gujarati")


def test_mark_user_alert_read_commits_only_an_owned_match():
    session = MagicMock()
    alert = SimpleNamespace(is_read=False)
    session.query.return_value.filter.return_value.first.return_value = alert

    assert mark_user_alert_read(session, "user-1", 7) is True
    assert alert.is_read is True
    session.commit.assert_called_once()


def test_mark_user_alert_read_does_not_commit_when_missing():
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None

    assert mark_user_alert_read(session, "user-1", 7) is False
    session.commit.assert_not_called()
