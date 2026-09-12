"""
app/alerts.py

Alerting module for the enforcement layer.

Every time the blocking middleware denies a request (BOLA, BFLA, or
rate-limit violation), it emits an Alert through the AlertManager.
Alerts are kept in memory for fast querying and also appended to
alerts.log for a persistent, human-readable record.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json

# Severity is inferred automatically from violation_type rather than
# passed in manually -- access-control breaches (BOLA/BFLA) are more
# serious than a single rate-limit hit.
SEVERITY_MAP = {
    "BOLA": "HIGH",
    "BFLA": "HIGH",
    "RATE_LIMIT": "MEDIUM",
}

DEFAULT_LOG_PATH = Path("alerts.log")


@dataclass
class Alert:
    timestamp: str        # ISO 8601, UTC
    violation_type: str   # "BOLA", "BFLA", "RATE_LIMIT"
    user_id: str
    context: str           # object_id, endpoint pattern, etc. -- whatever
                            # is most relevant for this violation type
    reason: str            # human-readable reason, reused from the
                            # AuthDecision / RateLimitDecision that
                            # triggered this alert
    severity: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AlertManager:
    """
    Collects alerts in memory and persists them to a log file.

    Usage:
        alerts = AlertManager()
        alerts.raise_alert(
            violation_type="BOLA",
            user_id="user_42",
            context="object_id=1007",
            reason="user '42' attempted to access object '1007' owned by 'user_7'",
        )
    """

    def __init__(self, log_path: Path = DEFAULT_LOG_PATH):
        self.log_path = Path(log_path)
        self._alerts: list[Alert] = []

    def raise_alert(
        self,
        violation_type: str,
        user_id: str,
        context: str,
        reason: str,
    ) -> Alert:
        alert = Alert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            violation_type=violation_type,
            user_id=user_id,
            context=context,
            reason=reason,
            severity=SEVERITY_MAP.get(violation_type, "LOW"),
        )
        self._alerts.append(alert)
        self._write_to_log(alert)
        return alert

    def get_recent_alerts(self, limit: int = 20) -> list[Alert]:
        """Return the most recent alerts, newest first."""
        return list(reversed(self._alerts[-limit:]))

    def get_alerts_by_type(self, violation_type: str) -> list[Alert]:
        return [a for a in self._alerts if a.violation_type == violation_type]

    def count(self) -> int:
        return len(self._alerts)

    def _write_to_log(self, alert: Alert) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(alert.to_json() + "\n")


# Shared, module-level instance so app/blocking_middleware.py and anything
# else in the app can raise/read alerts without passing an instance around.
alert_manager = AlertManager()