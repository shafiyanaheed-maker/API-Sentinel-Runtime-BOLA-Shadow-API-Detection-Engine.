from runtime.anomaly_detector import BehavioralAnomalyDetector
from runtime.traffic_parser import (
    ParsedRequest,
    ParsedResponse,
    TrafficEvent,
)


def create_event(
    path="/users/101",
    method="GET",
    status_code=200,
):
    request = ParsedRequest(
        method=method,
        path=path,
    )

    response = ParsedResponse(
        status_code=status_code,
    )

    return TrafficEvent(
        request=request,
        response=response,
    )


def test_normal_request_is_not_anomalous():
    detector = BehavioralAnomalyDetector()

    result = detector.analyze(
        user_id=1,
        traffic_event=create_event(),
    )

    assert result.detected is False
    assert result.score == 0
    assert result.severity == "NORMAL"
    assert result.reasons == []


def test_request_burst_is_detected():
    detector = BehavioralAnomalyDetector()

    for _ in range(20):
        result = detector.analyze(
            user_id=1,
            traffic_event=create_event(),
        )

    assert result.detected is True
    assert result.score >= 30
    assert result.severity in {
        "SUSPICIOUS",
        "HIGH",
        "CRITICAL",
    }
    assert any(
        "request frequency" in reason.lower()
        for reason in result.reasons
    )


def test_endpoint_diversity_is_detected():
    detector = BehavioralAnomalyDetector()

    for index in range(10):
        result = detector.analyze(
            user_id=1,
            traffic_event=create_event(
                path=f"/api/resource{index}",
            ),
        )

    assert result.detected is True
    assert result.score >= 30
    assert any(
        "endpoint diversity" in reason.lower()
        for reason in result.reasons
    )


def test_resource_enumeration_is_detected():
    detector = BehavioralAnomalyDetector()

    for resource_id in range(1, 9):
        result = detector.analyze(
            user_id=1,
            traffic_event=create_event(
                path=f"/users/{resource_id}",
            ),
        )

    assert result.detected is True
    assert result.score >= 30
    assert any(
        "resource enumeration" in reason.lower()
        for reason in result.reasons
    )


def test_high_error_rate_is_detected():
    detector = BehavioralAnomalyDetector()

    for _ in range(5):
        result = detector.analyze(
            user_id=1,
            traffic_event=create_event(
                path="/api/orders",
                status_code=500,
            ),
        )

    assert result.detected is True
    assert result.score >= 30
    assert any(
        "error rate" in reason.lower()
        for reason in result.reasons
    )


def test_behavior_is_tracked_per_user():
    detector = BehavioralAnomalyDetector()

    for _ in range(10):
        detector.analyze(
            user_id=1,
            traffic_event=create_event(
                path="/api/resource",
            ),
        )

    result = detector.analyze(
        user_id=2,
        traffic_event=create_event(
            path="/api/resource",
        ),
    )

    assert result.detected is False
    assert result.score == 0
    assert result.severity == "NORMAL"