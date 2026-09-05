from runtime.analyzer import analyze_request
from runtime.models import APIRequest
from runtime.traffic_parser import parse_request


def test_parsed_bola_request_reaches_runtime_analyzer():
    raw_request = (
        "GET /users/102 HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    )

    parsed_request = parse_request(raw_request)

    request = APIRequest(
        method=parsed_request.method,
        path=parsed_request.path,
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is True
    assert any(threat["type"] == "BOLA" for threat in result.threats)
    assert result.severity == "HIGH"


def test_parsed_bfla_request_reaches_runtime_analyzer():
    raw_request = (
        "DELETE /admin/users HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    )

    parsed_request = parse_request(raw_request)

    request = APIRequest(
        method=parsed_request.method,
        path=parsed_request.path,
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is True
    assert any(threat["type"] == "BFLA" for threat in result.threats)
    assert result.severity == "HIGH"


def test_parsed_legitimate_request_passes_analysis():
    raw_request = (
        "GET /users/101 HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    )

    parsed_request = parse_request(raw_request)

    request = APIRequest(
        method=parsed_request.method,
        path=parsed_request.path,
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is False
    assert result.threats == []
    assert result.severity == "LOW"


def test_parsed_request_with_body_reaches_analyzer():
    raw_request = (
        "POST /users HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"name": "test-user"}'
    )

    parsed_request = parse_request(raw_request)

    request = APIRequest(
        method=parsed_request.method,
        path=parsed_request.path,
        authenticated_user_id=101,
        user_role="user",
    )

    result = analyze_request(request)

    assert result.detected is False
    assert result.threats == []