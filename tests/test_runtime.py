from runtime.analyzer import analyze_request
from runtime.models import APIRequest


def test_authorized_request():
    request = APIRequest(
        method="GET",
        path="/users/101",
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is False
    assert result.threats == []
    assert result.severity == "LOW"


def test_bola_attack_detected():
    request = APIRequest(
        method="GET",
        path="/users/102",
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is True
    assert len(result.threats) == 1
    assert result.threats[0]["type"] == "BOLA"
    assert result.severity == "HIGH"


def test_bfla_attack_detected():
    request = APIRequest(
        method="GET",
        path="/admin/users",
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is True
    assert len(result.threats) == 1
    assert result.threats[0]["type"] == "BFLA"
    assert result.severity == "HIGH"


def test_bola_and_bfla_attacks_detected_together():
    request = APIRequest(
        method="GET",
        path="/users/102",
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is True
    assert any(
        threat["type"] == "BOLA"
        for threat in result.threats
    )


def test_unknown_endpoint_is_not_detected():
    request = APIRequest(
        method="GET",
        path="/health",
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is False
    assert result.threats == []
    assert result.severity == "LOW"