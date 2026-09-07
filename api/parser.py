import json
import re
from typing import Any


SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "proxy-authorization",
}


def normalize_path(path: str) -> str:
    """Remove query strings and normalize a runtime URL path."""
    if not path:
        return "/"
    return "/" + path.split("?", 1)[0].lstrip("/")


def parse_body(body: Any) -> Any:
    """Decode JSON strings while leaving ordinary text unchanged."""
    if body is None or isinstance(body, (dict, list, int, float, bool)):
        return body

    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    return str(body)


def mask_headers(headers: dict[str, Any] | None) -> dict[str, Any]:
    """Mask credentials/secrets before traffic is persisted."""
    if not headers:
        return {}

    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


def extract_user_object_ids(
    path: str,
    body: Any = None,
    headers: dict[str, Any] | None = None,
) -> tuple[str | None, str | None]:
    """
    Extract common user/object identifiers for downstream BOLA analysis.

    This is intentionally heuristic. The existing detection_engine remains
    responsible for the actual authorization decision.
    """
    path = normalize_path(path)
    user_id = None
    object_id = None

    user_match = re.search(r"/users?/([^/]+)", path, re.IGNORECASE)
    if user_match:
        user_id = user_match.group(1)

    object_match = re.search(
        r"/(?:objects?|orders?|accounts?|profiles?|documents?|files?)/([^/]+)",
        path,
        re.IGNORECASE,
    )
    if object_match:
        object_id = object_match.group(1)

    parsed_body = parse_body(body)
    if isinstance(parsed_body, dict):
        user_id = user_id or parsed_body.get("user_id") or parsed_body.get("userId")
        object_id = (
            object_id
            or parsed_body.get("object_id")
            or parsed_body.get("objectId")
        )

    if headers:
        user_id = user_id or headers.get("x-user-id") or headers.get("X-User-ID")

    return (
        str(user_id) if user_id is not None else None,
        str(object_id) if object_id is not None else None,
    )


def serialize_body(body: Any) -> str | None:
    parsed = parse_body(body)
    if parsed is None:
        return None
    if isinstance(parsed, str):
        return parsed
    return json.dumps(parsed, ensure_ascii=False)
