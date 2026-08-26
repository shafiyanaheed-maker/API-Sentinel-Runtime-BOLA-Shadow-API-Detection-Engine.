HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE"
}

RESOURCE_PATTERNS = [
    r"/users/(\d+)",
    r"/accounts/(\d+)",
    r"/orders/(\d+)",
    r"/profiles/(\d+)",
    r"/documents/(\d+)",
    r"/files/(\d+)"
]


# User → resource ownership relationships
RESOURCE_OWNERSHIP = {
    101: {101, 105},
    102: {102, 106},
    103: {103, 107}
}