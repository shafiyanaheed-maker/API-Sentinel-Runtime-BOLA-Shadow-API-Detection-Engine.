import pytest

from runtime.traffic_parser import (
    ParsedRequest,
    ParsedResponse,
    TrafficEvent,
    parse_request,
    parse_response,
    parse_traffic,
)


def test_parse_http_request():
    raw_request = (
        "GET /api/users/101 HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "Authorization: Bearer test-token\r\n"
        "\r\n"
    )

    result = parse_request(raw_request)

    assert isinstance(result, ParsedRequest)
    assert result.method == "GET"
    assert result.path == "/api/users/101"
    assert result.headers["Host"] == "example.com"
    assert result.headers["Authorization"] == "Bearer test-token"
    assert result.body is None


def test_parse_http_request_with_body():
    raw_request = (
        "POST /api/users HTTP/1.1\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"name": "Shaafiya"}'
    )

    result = parse_request(raw_request)

    assert result.method == "POST"
    assert result.path == "/api/users"
    assert result.headers["Content-Type"] == "application/json"
    assert result.body == '{"name": "Shaafiya"}'


def test_parse_http_response():
    raw_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"id": 101}'
    )

    result = parse_response(raw_response)

    assert isinstance(result, ParsedResponse)
    assert result.status_code == 200
    assert result.headers["Content-Type"] == "application/json"
    assert result.body == '{"id": 101}'


def test_parse_http_error_response():
    raw_response = (
        "HTTP/1.1 403 Forbidden\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"error": "forbidden"}'
    )

    result = parse_response(raw_response)

    assert result.status_code == 403
    assert result.body == '{"error": "forbidden"}'


def test_parse_complete_traffic_event():
    raw_request = (
        "GET /api/orders/42 HTTP/1.1\r\n"
        "Host: example.com\r\n"
        "\r\n"
    )

    raw_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "\r\n"
        '{"id": 42}'
    )

    result = parse_traffic(raw_request, raw_response)

    assert isinstance(result, TrafficEvent)
    assert result.request.method == "GET"
    assert result.request.path == "/api/orders/42"
    assert result.response.status_code == 200
    assert result.response.body == '{"id": 42}'


def test_empty_request_is_rejected():
    with pytest.raises(ValueError):
        parse_request("")


def test_empty_response_is_rejected():
    with pytest.raises(ValueError):
        parse_response("")


def test_invalid_request_line_is_rejected():
    with pytest.raises(ValueError):
        parse_request("INVALID")


def test_invalid_response_status_is_rejected():
    with pytest.raises(ValueError):
        parse_response(
            "HTTP/1.1 NOT_A_STATUS\r\n"
            "\r\n"
        )