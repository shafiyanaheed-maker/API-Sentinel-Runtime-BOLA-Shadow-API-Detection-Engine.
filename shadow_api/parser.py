import json
from pathlib import Path

import yaml


HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
}


def load_openapi_spec(file_path):
    """Load an OpenAPI specification from JSON or YAML."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"OpenAPI specification not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        suffix = path.suffix.lower()

        if suffix == ".json":
            spec = json.load(file)

        elif suffix in {".yaml", ".yml"}:
            spec = yaml.safe_load(file)

        else:
            raise ValueError("Unsupported file format. Use JSON, YAML, or YML.")

    if not isinstance(spec, dict):
        raise ValueError("OpenAPI specification must contain a JSON/YAML object.")

    if "paths" not in spec:
        raise ValueError("OpenAPI specification does not contain a 'paths' section.")

    return spec


def normalize_path(path):
    """Normalize an API path for consistent endpoint comparison."""
    if not isinstance(path, str):
        raise ValueError("API path must be a string.")

    normalized = path.strip()

    if not normalized:
        raise ValueError("API path cannot be empty.")

    if not normalized.startswith("/"):
        normalized = f"/{normalized}"

    while "//" in normalized:
        normalized = normalized.replace("//", "/")

    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized[:-1]

    return normalized


def extract_endpoints(spec):
    """Extract documented HTTP endpoints from an OpenAPI specification."""
    if not isinstance(spec, dict):
        raise ValueError("OpenAPI specification must be a dictionary.")

    endpoints = set()
    paths = spec.get("paths", {})

    if not isinstance(paths, dict):
        raise ValueError("OpenAPI 'paths' must be a dictionary.")

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue

        normalized_path = normalize_path(path)

        for method in methods:
            method_upper = str(method).upper()

            if method_upper in HTTP_METHODS:
                endpoints.add(f"{method_upper} {normalized_path}")

    return endpoints