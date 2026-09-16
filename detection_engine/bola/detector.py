import re

from .rules import HTTP_METHODS, RESOURCE_PATTERNS, RESOURCE_OWNERSHIP


def extract_resource_id(path: str):
    for pattern in RESOURCE_PATTERNS:
        match = re.search(pattern, path)

        if match:
            return int(match.group(1))

    return None


def detect_bola(
    method: str,
    path: str,
    authenticated_user_id: int
):
    method = method.upper()

    if method not in HTTP_METHODS:
        return {
            "detected": False,
            "reason": "HTTP method is not monitored"
        }

    resource_id = extract_resource_id(path)

    if resource_id is None:
        return {
            "detected": False,
            "reason": "No resource ID detected"
        }

    owned_resources = RESOURCE_OWNERSHIP.get(
        authenticated_user_id,
        set()
    )

    if resource_id not in owned_resources:
        return {
            "detected": True,
            "type": "BOLA",
            "severity": "HIGH",
            "reason": "Unauthorized object access detected",
            "user_id": authenticated_user_id,
            "resource_id": resource_id
        }

    return {
        "detected": False,
        "reason": "Authorized object access",
        "user_id": authenticated_user_id,
        "resource_id": resource_id
    }