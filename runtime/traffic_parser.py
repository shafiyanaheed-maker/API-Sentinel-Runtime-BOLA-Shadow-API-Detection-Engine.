from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ParsedRequest:
    """Normalized representation of an observed HTTP request."""

    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None


@dataclass
class ParsedResponse:
    """Normalized representation of an observed HTTP response."""

    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None


@dataclass
class TrafficEvent:
    """Combined request and response captured from API traffic."""

    request: ParsedRequest
    response: ParsedResponse


def parse_request(raw_request: str) -> ParsedRequest:
    """Parse a raw HTTP request into a normalized request object."""
    if not isinstance(raw_request, str) or not raw_request.strip():
        raise ValueError("Raw request cannot be empty.")

    sections = raw_request.replace("\r\n", "\n").split("\n\n", 1)
    header_section = sections[0]

    body = sections[1] if len(sections) > 1 and sections[1] else None

    lines = header_section.split("\n")

    if not lines or not lines[0].strip():
        raise ValueError("HTTP request line is missing.")

    request_line = lines[0].split()

    if len(request_line) < 2:
        raise ValueError("Invalid HTTP request line.")

    method = request_line[0].upper()
    path = request_line[1]

    headers = {}

    for line in lines[1:]:
        if ":" not in line:
            continue

        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()

    return ParsedRequest(
        method=method,
        path=path,
        headers=headers,
        body=body,
    )


def parse_response(raw_response: str) -> ParsedResponse:
    """Parse a raw HTTP response into a normalized response object."""
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise ValueError("Raw response cannot be empty.")

    sections = raw_response.replace("\r\n", "\n").split("\n\n", 1)
    header_section = sections[0]

    body = sections[1] if len(sections) > 1 and sections[1] else None

    lines = header_section.split("\n")

    if not lines or not lines[0].strip():
        raise ValueError("HTTP response line is missing.")

    response_line = lines[0].split()

    if len(response_line) < 2:
        raise ValueError("Invalid HTTP response line.")

    try:
        status_code = int(response_line[1])
    except ValueError as exc:
        raise ValueError("Invalid HTTP response status code.") from exc

    headers = {}

    for line in lines[1:]:
        if ":" not in line:
            continue

        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()

    return ParsedResponse(
        status_code=status_code,
        headers=headers,
        body=body,
    )


def parse_traffic(raw_request: str, raw_response: str) -> TrafficEvent:
    """Reconstruct a complete request/response traffic event."""
    request = parse_request(raw_request)
    response = parse_response(raw_response)

    return TrafficEvent(
        request=request,
        response=response,
    )