"""
tests/test_audit.py

Unit tests for AuditLogger (app/audit.py). Each test uses its own temporary
SQLite file so tests are isolated from each other and from the real
data/audit.db used by the running app.
"""

import pytest
from pathlib import Path

from app.audit import AuditLogger


@pytest.fixture
def audit_logger(tmp_path: Path) -> AuditLogger:
    """Fresh AuditLogger backed by a temp SQLite file for each test."""
    db_path = tmp_path / "test_audit.db"
    return AuditLogger(db_path=db_path)


def test_append_creates_entry(audit_logger: AuditLogger):
    entry = audit_logger.append(
        user_id="user_a",
        endpoint="/api/orders/{id}",
        method="GET",
        allowed=True,
        reason="all checks passed",
    )

    assert entry.user_id == "user_a"
    assert entry.endpoint == "/api/orders/{id}"
    assert entry.method == "GET"
    assert entry.allowed is True
    assert entry.reason == "all checks passed"
    assert entry.timestamp  # non-empty ISO timestamp string


def test_query_returns_entries_in_reverse_chronological_order(audit_logger: AuditLogger):
    audit_logger.append(user_id="user_a", endpoint="/health", method="GET", allowed=True, reason="ok")
    audit_logger.append(user_id="user_a", endpoint="/api/products", method="GET", allowed=True, reason="ok")
    audit_logger.append(user_id="user_a", endpoint="/api/orders/{id}", method="GET", allowed=False, reason="blocked")

    entries = audit_logger.query(limit=10)

    assert len(entries) == 3
    # Most recent entry (the blocked one) should come first
    assert entries[0].endpoint == "/api/orders/{id}"
    assert entries[0].allowed is False
    assert entries[-1].endpoint == "/health"


def test_query_filters_by_user_id(audit_logger: AuditLogger):
    audit_logger.append(user_id="user_a", endpoint="/health", method="GET", allowed=True, reason="ok")
    audit_logger.append(user_id="user_b", endpoint="/health", method="GET", allowed=True, reason="ok")

    entries = audit_logger.query(user_id="user_b")

    assert len(entries) == 1
    assert entries[0].user_id == "user_b"


def test_query_filters_by_allowed(audit_logger: AuditLogger):
    audit_logger.append(user_id="user_a", endpoint="/health", method="GET", allowed=True, reason="ok")
    audit_logger.append(
        user_id="user_a", endpoint="/api/orders/{id}", method="GET",
        allowed=False, reason="Rate limit exceeded",
    )

    blocked_only = audit_logger.query(allowed=False)
    allowed_only = audit_logger.query(allowed=True)

    assert len(blocked_only) == 1
    assert blocked_only[0].reason == "Rate limit exceeded"
    assert len(allowed_only) == 1
    assert allowed_only[0].endpoint == "/health"


def test_query_respects_limit(audit_logger: AuditLogger):
    for i in range(10):
        audit_logger.append(
            user_id="user_a", endpoint="/health", method="GET",
            allowed=True, reason=f"call {i}",
        )

    entries = audit_logger.query(limit=3)

    assert len(entries) == 3


def test_query_with_no_matches_returns_empty_list(audit_logger: AuditLogger):
    audit_logger.append(user_id="user_a", endpoint="/health", method="GET", allowed=True, reason="ok")

    entries = audit_logger.query(user_id="nonexistent_user")

    assert entries == []