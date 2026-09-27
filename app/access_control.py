"""
access_control.py

In-memory allowlist/blocklist for API-Sentinel, checked before any other
enforcement logic runs.

- Blocklisted users/IPs are rejected immediately (403), regardless of
  what any other check would decide -- useful for instantly cutting off
  an attacker spotted via the admin dashboard, without a restart.
- Allowlisted users/IPs bypass every other check (rate limits, BFLA,
  BOLA) -- useful for trusted internal traffic (health checks, admin
  tooling) that shouldn't be throttled or blocked by mistake.

This is intentionally in-memory only (resets on restart), matching the
pattern already used by AlertManager and the rate limiters in this app.
A persistent version could swap this out for a database-backed store
without changing the public interface.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccessDecision:
    matched: bool          # True if this entity is on either list
    listed_as: str | None  # "blocked", "allowed", or None
    reason: str


class AccessControlList:
    def __init__(self):
        self._blocked_users: set[str] = set()
        self._blocked_ips: set[str] = set()
        self._allowed_users: set[str] = set()
        self._allowed_ips: set[str] = set()

    # -- Blocklist management --

    def block_user(self, user_id: str) -> None:
        self._blocked_users.add(user_id)

    def unblock_user(self, user_id: str) -> None:
        self._blocked_users.discard(user_id)

    def block_ip(self, ip: str) -> None:
        self._blocked_ips.add(ip)

    def unblock_ip(self, ip: str) -> None:
        self._blocked_ips.discard(ip)

    # -- Allowlist management --

    def allow_user(self, user_id: str) -> None:
        self._allowed_users.add(user_id)

    def unallow_user(self, user_id: str) -> None:
        self._allowed_users.discard(user_id)

    def allow_ip(self, ip: str) -> None:
        self._allowed_ips.add(ip)

    def unallow_ip(self, ip: str) -> None:
        self._allowed_ips.discard(ip)

    # -- Checks --

    def check(self, user_id: str, ip: str) -> AccessDecision:
        """
        Blocklist takes priority over allowlist -- if an entity is
        somehow on both lists (e.g. added to blocklist after already
        being allowlisted), it stays blocked. Fail toward caution.
        """
        if user_id in self._blocked_users:
            return AccessDecision(
                matched=True, listed_as="blocked",
                reason=f"user '{user_id}' is on the blocklist",
            )
        if ip in self._blocked_ips:
            return AccessDecision(
                matched=True, listed_as="blocked",
                reason=f"IP '{ip}' is on the blocklist",
            )
        if user_id in self._allowed_users:
            return AccessDecision(
                matched=True, listed_as="allowed",
                reason=f"user '{user_id}' is on the allowlist",
            )
        if ip in self._allowed_ips:
            return AccessDecision(
                matched=True, listed_as="allowed",
                reason=f"IP '{ip}' is on the allowlist",
            )
        return AccessDecision(matched=False, listed_as=None, reason="not listed")

    def snapshot(self) -> dict:
        """Current list contents, for the admin dashboard."""
        return {
            "blocked_users": sorted(self._blocked_users),
            "blocked_ips": sorted(self._blocked_ips),
            "allowed_users": sorted(self._allowed_users),
            "allowed_ips": sorted(self._allowed_ips),
        }


# Shared, module-level instance, matching the pattern used by
# alert_manager and audit_logger.
access_control = AccessControlList()
