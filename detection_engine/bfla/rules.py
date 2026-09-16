HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE"
}

# Endpoints mapped to the minimum role required
ENDPOINT_ROLES = {
    "/admin/users": "admin",
    "/admin/settings": "admin",
    "/admin/logs": "admin",
    "/users": "user",
    "/profile": "user"
}

ROLE_LEVELS = {
    "user": 1,
    "admin": 2
}
