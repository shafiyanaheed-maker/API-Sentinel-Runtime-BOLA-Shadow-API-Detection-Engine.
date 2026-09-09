from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Deque, Dict, Set
import re
import time

from runtime.traffic_parser import TrafficEvent


@dataclass
class UserBehavior:
    """Stores recent API behavior for a single user."""

    request_times: Deque[float] = field(default_factory=deque)
    endpoints: Deque[str] = field(default_factory=deque)
    resource_paths: Deque[str] = field(default_factory=deque)
    status_codes: Deque[int] = field(default_factory=deque)


@dataclass
class AnomalyResult:
    """Result returned by the behavioral anomaly detector."""

    detected: bool
    score: int
    severity: str
    reasons: list


class BehavioralAnomalyDetector:
    """
    Detect unusual API behavior using an explainable rule-based score.

    Signals:
    - Request bursts
    - Unusual endpoint diversity
    - Rapid resource-ID changes
    - High error rate
    """

    WINDOW_SECONDS = 60
    MAX_HISTORY = 100

    BURST_THRESHOLD = 20
    ENDPOINT_DIVERSITY_THRESHOLD = 10
    RESOURCE_ENUMERATION_THRESHOLD = 8
    ERROR_RATE_THRESHOLD = 0.50

    def __init__(self):
        self.user_history: Dict[int, UserBehavior] = defaultdict(UserBehavior)

    def _extract_resource_pattern(self, path: str) -> str:
        """
        Replace numeric resource IDs with {id}.

        Example:
        /users/101/orders/5001
        becomes:
        /users/{id}/orders/{id}
        """

        return re.sub(r"/\d+", "/{id}", path)

    def _cleanup_history(
        self,
        behavior: UserBehavior,
        now: float,
    ) -> None:
        """Remove request history older than the configured window."""

        while (
            behavior.request_times
            and now - behavior.request_times[0] > self.WINDOW_SECONDS
        ):
            behavior.request_times.popleft()
            behavior.endpoints.popleft()
            behavior.resource_paths.popleft()
            behavior.status_codes.popleft()

    def analyze(
        self,
        user_id: int,
        traffic_event: TrafficEvent,
    ) -> AnomalyResult:
        """Analyze one API traffic event and return an anomaly result."""

        now = time.time()
        behavior = self.user_history[user_id]

        self._cleanup_history(behavior, now)

        request = traffic_event.request
        response = traffic_event.response

        endpoint_pattern = self._extract_resource_pattern(
            request.path
        )

        behavior.request_times.append(now)
        behavior.endpoints.append(endpoint_pattern)
        behavior.resource_paths.append(request.path)
        behavior.status_codes.append(response.status_code)

        while len(behavior.request_times) > self.MAX_HISTORY:
            behavior.request_times.popleft()
            behavior.endpoints.popleft()
            behavior.resource_paths.popleft()
            behavior.status_codes.popleft()

        score = 0
        reasons = []

        # ---------------------------------------------------------
        # 1. Request burst detection
        # ---------------------------------------------------------

        request_count = len(behavior.request_times)

        if request_count >= self.BURST_THRESHOLD:
            score += 30
            reasons.append(
                f"High request frequency: {request_count} requests "
                f"within {self.WINDOW_SECONDS} seconds"
            )

        # ---------------------------------------------------------
        # 2. Endpoint diversity detection
        # ---------------------------------------------------------

        unique_endpoints: Set[str] = set(behavior.endpoints)

        if len(unique_endpoints) >= self.ENDPOINT_DIVERSITY_THRESHOLD:
            score += 30
            reasons.append(
                f"Unusual endpoint diversity: "
                f"{len(unique_endpoints)} different endpoint patterns"
            )

        # ---------------------------------------------------------
        # 3. Resource enumeration detection
        # ---------------------------------------------------------

        resource_ids = []

        for path in behavior.resource_paths:
            matches = re.findall(r"/(\d+)(?:/|$)", path)

            for resource_id in matches:
                resource_ids.append(resource_id)

        unique_resource_ids = set(resource_ids)

        if len(unique_resource_ids) >= self.RESOURCE_ENUMERATION_THRESHOLD:
            score += 30
            reasons.append(
                f"Possible resource enumeration: "
                f"{len(unique_resource_ids)} different resource IDs accessed"
            )

        # ---------------------------------------------------------
        # 4. Error-rate detection
        # ---------------------------------------------------------

        error_count = sum(
            1
            for status_code in behavior.status_codes
            if status_code >= 400
        )

        total_responses = len(behavior.status_codes)

        if total_responses > 0:
            error_rate = error_count / total_responses

            if (
                total_responses >= 5
                and error_rate >= self.ERROR_RATE_THRESHOLD
            ):
                score += 30
                reasons.append(
                    f"High API error rate: "
                    f"{error_rate * 100:.0f}% of recent requests "
                    f"returned errors"
                )

        # ---------------------------------------------------------
        # Score normalization
        # ---------------------------------------------------------

        score = min(score, 100)

        if score >= 80:
            severity = "CRITICAL"
        elif score >= 60:
            severity = "HIGH"
        elif score >= 30:
            severity = "SUSPICIOUS"
        else:
            severity = "NORMAL"

        detected = score >= 30

        return AnomalyResult(
            detected=detected,
            score=score,
            severity=severity,
            reasons=reasons,
        )


# -------------------------------------------------------------
# Shared detector instance
# -------------------------------------------------------------

_default_detector = BehavioralAnomalyDetector()


def detect_behavioral_anomaly(
    user_id: int,
    traffic_event: TrafficEvent,
) -> AnomalyResult:
    """Detect behavioral anomalies using the shared detector."""

    return _default_detector.analyze(
        user_id=user_id,
        traffic_event=traffic_event,
    )