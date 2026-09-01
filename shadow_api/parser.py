import json
import yaml


def load_openapi_spec(file_path):
    with open(file_path, "r") as file:

        if file_path.endswith(".json"):
            spec = json.load(file)

        elif file_path.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(file)

        else:
            raise ValueError("Unsupported file format")

    return spec


def extract_endpoints(spec):

    endpoints = set()

    paths = spec.get("paths", {})

    for path, methods in paths.items():

        for method in methods.keys():

            endpoints.add(
                f"{method.upper()} {path}"
            )

    return endpoints