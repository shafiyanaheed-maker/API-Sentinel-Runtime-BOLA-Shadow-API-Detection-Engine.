"""
tests/test_stats.py

Unit tests for AlertManager.get_stats() (app/alerts.py). Uses a fresh
AlertManager with a temp log file so tests don't touch the real
alerts.log used by the running app.
"""

import pytest
from pathlib import Path

from app.alerts import AlertManager


@pytest.fixture
def alert_manager(tmp_path: Path) -> AlertManager:
    """Fresh AlertManager backed by a temp log file for each test."""
    log_path = tmp_path / "test_alerts.log"
    return AlertManager(log_path=log_path)


def test_get_stats_with_no_alerts(alert_manager: AlertManager):
    stats = alert_manager.get_stats()

    assert stats["total_alerts"] == 0
    assert stats["by_violation_type"] == {}
    assert stats["recent_alerts"] == []


def test_get_stats_total_count(alert_manager: AlertManager):
    alert_manager.raise_alert(
        violation_type="BOLA", user_id="user_a", context="test", reason="test"
    )
    alert_manager.raise_alert(
        violation_type="BFLA", user_id="user_b", context="test", reason="test"
    )

    stats = alert_manager.get_stats()

    assert stats["total_alerts"] == 2


def test_get_stats_breakdown_by_violation_type(alert_manager: AlertManager):
    alert_manager.raise_alert(
        violation_type="BOLA", user_id="user_a", context="test", reason="test"
    )
    alert_manager.raise_alert(
        violation_type="BOLA", user_id="user_b", context="test", reason="test"
    )
    alert_manager.raise_alert(
        violation_type="RATE_LIMIT", user_id="user_c", context="test", reason="test"
    )

    stats = alert_manager.get_stats()

    assert stats["by_violation_type"] == {"BOLA": 2, "RATE_LIMIT": 1}


def test_get_stats_recent_alerts_limited_to_five(alert_manager: AlertManager):
    for i in range(8):
        alert_manager.raise_alert(
            violation_type="BOLA", user_id=f"user_{i}", context="test", reason="test"
        )

    stats = alert_manager.get_stats()

    assert len(stats["recent_alerts"]) == 5


def test_get_stats_recent_alerts_are_newest_first(alert_manager: AlertManager):
    alert_manager.raise_alert(
        violation_type="BOLA", user_id="first", context="test", reason="test"
    )
    alert_manager.raise_alert(
        violation_type="BFLA", user_id="second", context="test", reason="test"
    )

    stats = alert_manager.get_stats()

    assert stats["recent_alerts"][0]["user_id"] == "second"
    assert stats["recent_alerts"][1]["user_id"] == "first"


def test_get_stats_recent_alerts_are_full_dicts(alert_manager: AlertManager):
    alert_manager.raise_alert(
        violation_type="BOLA", user_id="user_a", context="ctx", reason="reason text"
    )

    stats = alert_manager.get_stats()
    entry = stats["recent_alerts"][0]

    assert entry["violation_type"] == "BOLA"
    assert entry["user_id"] == "user_a"
    assert entry["context"] == "ctx"
    assert entry["reason"] == "reason text"
    assert entry["severity"] == "HIGH"
    assert "timestamp" in entry
