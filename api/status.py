"""API-Sentinel API package."""

PROJECT_NAME = "API-Sentinel"
PROJECT_STATUS = "development"


def get_project_status():
    return {
        "project": PROJECT_NAME,
        "status": PROJECT_STATUS,
    }
