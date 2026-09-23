"""
tests/test_notifications.py

Unit tests for WebhookNotifier (app/notifications.py). All HTTP calls are
mocked -- these tests never make a real network request.
"""

from unittest.mock import patch, Mock

import requests

from app.notifications import WebhookNotifier


def test_send_with_no_url_configured_returns_false():
    notifier = WebhookNotifier(webhook_url=None)

    result = notifier.send("test message")

    assert result is False


def test_send_with_no_url_does_not_call_requests():
    notifier = WebhookNotifier(webhook_url=None)

    with patch("app.notifications.requests.post") as mock_post:
        notifier.send("test message")
        mock_post.assert_not_called()


def test_send_posts_correct_payload_when_url_configured():
    notifier = WebhookNotifier(webhook_url="https://hooks.example.com/webhook")

    mock_response = Mock(status_code=200)
    with patch("app.notifications.requests.post", return_value=mock_response) as mock_post:
        result = notifier.send("🚨 test alert")

        mock_post.assert_called_once_with(
            "https://hooks.example.com/webhook",
            json={"text": "🚨 test alert"},
            timeout=5.0,
        )
        assert result is True


def test_send_returns_false_on_non_2xx_response():
    notifier = WebhookNotifier(webhook_url="https://hooks.example.com/webhook")

    mock_response = Mock(status_code=500, text="Internal Server Error")
    with patch("app.notifications.requests.post", return_value=mock_response):
        result = notifier.send("test message")

    assert result is False


def test_send_returns_false_and_does_not_raise_on_network_error():
    notifier = WebhookNotifier(webhook_url="https://hooks.example.com/webhook")

    with patch(
        "app.notifications.requests.post",
        side_effect=requests.RequestException("connection failed"),
    ):
        result = notifier.send("test message")

    assert result is False


def test_explicit_url_overrides_environment_variable(monkeypatch):
    monkeypatch.setenv("ALERT_WEBHOOK_URL", "https://env-url.example.com")

    notifier = WebhookNotifier(webhook_url="https://explicit-url.example.com")

    assert notifier.webhook_url == "https://explicit-url.example.com"


def test_falls_back_to_environment_variable_when_not_passed(monkeypatch):
    monkeypatch.setenv("ALERT_WEBHOOK_URL", "https://env-url.example.com")

    notifier = WebhookNotifier()

    assert notifier.webhook_url == "https://env-url.example.com"


def test_defaults_to_none_when_no_url_and_no_env_var(monkeypatch):
    monkeypatch.delenv("ALERT_WEBHOOK_URL", raising=False)

    notifier = WebhookNotifier()

    assert notifier.webhook_url is None
