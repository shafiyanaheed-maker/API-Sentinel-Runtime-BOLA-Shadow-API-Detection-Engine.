from .parser import normalize_path


def build_endpoint_signature(method, path):
    """Convert an observed HTTP request into a comparable endpoint signature."""
    if not isinstance(method, str) or not method.strip():
        raise ValueError("HTTP method cannot be empty.")

    normalized_method = method.strip().upper()
    normalized_path = normalize_path(path)

    return f"{normalized_method} {normalized_path}"


def extract_observed_endpoints(requests):
    """Extract unique endpoint signatures from observed API requests."""
    endpoints = set()

    for request in requests:
        if not isinstance(request, dict):
            raise ValueError("Each observed request must be a dictionary.")

        method = request.get("method")
        path = request.get("path")

        endpoints.add(build_endpoint_signature(method, path))

    return endpoints