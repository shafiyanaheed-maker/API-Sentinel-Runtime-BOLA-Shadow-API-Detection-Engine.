"""
notifications.py

Sends outbound alert notifications to an external webhook (Slack- or
Discord-compatible JSON payload), configured via the ALERT_WEBHOOK_URL
environment variable.

If ALERT_WEBHOOK_URL is not set, WebhookNotifier falls back to a safe
no-op: it just logs what it *would* have sent. This means the app runs
fine in local/dev/CI environments with zero external credentials, and a
real webhook can be plugged in later purely via configuration -- no code
changes needed.
"""

from __future__ import annotations

import os
import logging

import requests

logger = logging.getLogger("api_sentinel.notifications")


class WebhookNotifier:
    """
    Posts a Slack-compatible {"text": "..."} payload to a webhook URL.

    Usage:
        notifier = WebhookNotifier()
        notifier.send("🚨 BOLA violation by user_a on order 1005")
    """

    def __init__(self, webhook_url: str | None = None, timeout_seconds: float = 5.0):
        # Falls back to the environment variable if not passed explicitly,
        # so tests / callers can inject a fake URL without touching env vars.
        self.webhook_url = webhook_url if webhook_url is not None else os.environ.get(
            "ALERT_WEBHOOK_URL"
        )
        self.timeout_seconds = timeout_seconds

    def send(self, message: str) -> bool:
        """
        Attempt to send `message` to the configured webhook.

        Returns True if a send was attempted and succeeded (HTTP 2xx),
        False otherwise (no URL configured, network error, or non-2xx
        response). Never raises -- a notification failure should never
        take down the enforcement path that triggered it.
        """
        if not self.webhook_url:
            logger.info("[notify] no webhook configured, would send: %s", message)
            return False

        try:
            resp = requests.post(
                self.webhook_url,
                json={"text": message},
                timeout=self.timeout_seconds,
            )
            if 200 <= resp.status_code < 300:
                return True
            logger.warning(
                "[notify] webhook returned HTTP %s: %s", resp.status_code, resp.text
            )
            return False
        except requests.RequestException as exc:
            logger.warning("[notify] failed to send webhook notification: %s", exc)
            return False


# Shared, module-level instance -- mirrors the pattern used by
# alert_manager in app/alerts.py.
notifier = WebhookNotifier()
