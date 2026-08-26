from .rules import HTTP_METHODS, ENDPOINT_ROLES, ROLE_LEVELS


def detect_bfla(
    method: str,
    path: str,
    user_role: str
):
    method = method.upper()
    user_role = user_role.lower()

    # Ignore unsupported HTTP methods
    if method not in HTTP_METHODS:
        return {
            "detected": False,
            "reason": "HTTP method is not monitored"
        }

    # Find the endpoint's required role
    required_role = ENDPOINT_ROLES.get(path)

    if required_role is None:
        return {
            "detected": False,
            "reason": "Endpoint is not protected"
        }

    user_level = ROLE_LEVELS.get(user_role, 0)
    required_level = ROLE_LEVELS.get(required_role, 0)

    # User does not have enough privileges
    if user_level < required_level:
        return {
            "detected": True,
            "type": "BFLA",
            "severity": "HIGH",
            "reason": "Unauthorized function access detected",
            "method": method,
            "path": path,
            "user_role": user_role,
            "required_role": required_role
        }

    return {
        "detected": False,
        "reason": "Authorized function access",
        "method": method,
        "path": path,
        "user_role": user_role
    }
