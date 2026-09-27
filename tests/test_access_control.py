"""
tests/test_access_control.py

Unit tests for AccessControlList (app/access_control.py). Tests the class
directly, without going through the HTTP layer.
"""

import pytest

from app.access_control import AccessControlList


@pytest.fixture
def acl() -> AccessControlList:
    return AccessControlList()


def test_unlisted_entity_is_not_matched(acl: AccessControlList):
    decision = acl.check("user_a", "1.2.3.4")

    assert decision.matched is False
    assert decision.listed_as is None


def test_blocked_user_is_matched_as_blocked(acl: AccessControlList):
    acl.block_user("attacker_1")

    decision = acl.check("attacker_1", "1.2.3.4")

    assert decision.matched is True
    assert decision.listed_as == "blocked"
    assert "attacker_1" in decision.reason


def test_blocked_ip_is_matched_as_blocked(acl: AccessControlList):
    acl.block_ip("9.9.9.9")

    decision = acl.check("some_user", "9.9.9.9")

    assert decision.matched is True
    assert decision.listed_as == "blocked"
    assert "9.9.9.9" in decision.reason


def test_allowed_user_is_matched_as_allowed(acl: AccessControlList):
    acl.allow_user("trusted_service")

    decision = acl.check("trusted_service", "1.2.3.4")

    assert decision.matched is True
    assert decision.listed_as == "allowed"


def test_allowed_ip_is_matched_as_allowed(acl: AccessControlList):
    acl.allow_ip("10.0.0.1")

    decision = acl.check("some_user", "10.0.0.1")

    assert decision.matched is True
    assert decision.listed_as == "allowed"


def test_blocklist_takes_priority_over_allowlist(acl: AccessControlList):
    """
    If a user somehow ends up on both lists, the blocklist wins --
    fail toward caution rather than accidentally letting a blocked
    entity back in.
    """
    acl.allow_user("user_x")
    acl.block_user("user_x")

    decision = acl.check("user_x", "1.2.3.4")

    assert decision.listed_as == "blocked"


def test_unblock_user_removes_from_blocklist(acl: AccessControlList):
    acl.block_user("attacker_1")
    acl.unblock_user("attacker_1")

    decision = acl.check("attacker_1", "1.2.3.4")

    assert decision.matched is False


def test_unblock_ip_removes_from_blocklist(acl: AccessControlList):
    acl.block_ip("9.9.9.9")
    acl.unblock_ip("9.9.9.9")

    decision = acl.check("some_user", "9.9.9.9")

    assert decision.matched is False


def test_unallow_user_removes_from_allowlist(acl: AccessControlList):
    acl.allow_user("trusted_service")
    acl.unallow_user("trusted_service")

    decision = acl.check("trusted_service", "1.2.3.4")

    assert decision.matched is False


def test_unallow_ip_removes_from_allowlist(acl: AccessControlList):
    acl.allow_ip("10.0.0.1")
    acl.unallow_ip("10.0.0.1")

    decision = acl.check("some_user", "10.0.0.1")

    assert decision.matched is False


def test_unblocking_nonexistent_entry_does_not_raise(acl: AccessControlList):
    # Should be a safe no-op, not an error
    acl.unblock_user("never_blocked")
    acl.unblock_ip("never_blocked_ip")
    acl.unallow_user("never_allowed")
    acl.unallow_ip("never_allowed_ip")


def test_snapshot_reflects_current_state(acl: AccessControlList):
    acl.block_user("attacker_1")
    acl.block_ip("9.9.9.9")
    acl.allow_user("trusted_service")
    acl.allow_ip("10.0.0.1")

    snapshot = acl.snapshot()

    assert snapshot == {
        "blocked_users": ["attacker_1"],
        "blocked_ips": ["9.9.9.9"],
        "allowed_users": ["trusted_service"],
        "allowed_ips": ["10.0.0.1"],
    }


def test_snapshot_is_sorted(acl: AccessControlList):
    acl.block_user("zebra")
    acl.block_user("apple")
    acl.block_user("mango")

    snapshot = acl.snapshot()

    assert snapshot["blocked_users"] == ["apple", "mango", "zebra"]


def test_empty_acl_snapshot(acl: AccessControlList):
    snapshot = acl.snapshot()

    assert snapshot == {
        "blocked_users": [],
        "blocked_ips": [],
        "allowed_users": [],
        "allowed_ips": [],
    }
