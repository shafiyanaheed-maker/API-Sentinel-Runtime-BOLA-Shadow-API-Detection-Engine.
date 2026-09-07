from collections import defaultdict
import re

from .parser import normalize_path


HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
}

PATH_ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(\d+|[0-9a-fA-F]{8,})(?![A-Za-z0-9])"
)


def _normalize_observed_path(path):
    """Normalize an observed API path."""
    normalized = normalize_path(path)

    parts = normalized.split("/")
    normalized_parts = []

    for part in parts:
        if not part:
            continue

        if PATH_ID_PATTERN.fullmatch(part):
            normalized_parts.append("{id}")
        else:
            normalized_parts.append(part)

    if not normalized_parts:
        return "/"

    return "/" + "/".join(normalized_parts)


def _build_parameter(name):
    """Create an OpenAPI path parameter definition."""
    return {
        "name": name,
        "in": "path",
        "required": True,
        "schema": {
            "type": "string",
        },
    }


def generate_openapi_schema(observed_requests, title="API-Sentinel Observed APIs"):
    """
    Generate an OpenAPI 3.0.3 schema from observed HTTP traffic.

    Each request should contain at least:
        method
        path

    Optional fields:
        status_code
        response_content_type
        request_content_type
    """
    if not isinstance(observed_requests, list):
        raise ValueError("Observed requests must be a list.")

    paths = defaultdict(set)
    metadata = defaultdict(lambda: {
        "status_codes": set(),
        "response_content_types": set(),
        "request_content_types": set(),
    })

    for request in observed_requests:
        if not isinstance(request, dict):
            raise ValueError("Each observed request must be a dictionary.")

        method = request.get("method")
        path = request.get("path")

        if not isinstance(method, str) or not method.strip():
            raise ValueError("HTTP method cannot be empty.")

        if method.strip().upper() not in HTTP_METHODS:
            continue

        normalized_method = method.strip().lower()
        normalized_path = _normalize_observed_path(path)

        paths[normalized_path].add(normalized_method)

        key = (normalized_path, normalized_method)

        if request.get("status_code") is not None:
            metadata[key]["status_codes"].add(
                str(request["status_code"])
            )

        if request.get("response_content_type"):
            metadata[key]["response_content_types"].add(
                str(request["response_content_type"])
            )

        if request.get("request_content_type"):
            metadata[key]["request_content_types"].add(
                str(request["request_content_type"])
            )

    generated_paths = {}

    for path in sorted(paths):
        generated_paths[path] = {}

        path_parameters = []

        if "{id}" in path:
            path_parameters.append(_build_parameter("id"))

        for method in sorted(paths[path]):
            operation = {
                "summary": f"Observed {method.upper()} {path}",
                "operationId": (
                    f"observed_{method}_{path.strip('/').replace('/', '_')}"
                    .replace("{", "")
                    .replace("}", "")
                    or f"observed_{method}_root"
                ),
                "responses": {
                    "200": {
                        "description": "Observed successful response",
                    }
                },
            }

            if path_parameters:
                operation["parameters"] = path_parameters

            key = (path, method)
            info = metadata[key]

            if info["status_codes"]:
                operation["responses"] = {
                    code: {
                        "description": f"Observed HTTP {code} response"
                    }
                    for code in sorted(info["status_codes"])
                }

            if info["request_content_types"]:
                content_type = sorted(
                    info["request_content_types"]
                )[0]

                operation["requestBody"] = {
                    "content": {
                        content_type: {
                            "schema": {
                                "type": "object",
                            }
                        }
                    }
                }

            if info["response_content_types"]:
                content_type = sorted(
                    info["response_content_types"]
                )[0]

                response_code = next(
                    iter(operation["responses"])
                )

                operation["responses"][response_code]["content"] = {
                    content_type: {
                        "schema": {
                            "type": "object",
                        }
                    }
                }

            generated_paths[path][method] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": "1.0.0",
        },
        "paths": generated_paths,
    }