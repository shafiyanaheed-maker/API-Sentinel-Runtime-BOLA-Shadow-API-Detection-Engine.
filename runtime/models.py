from dataclasses import dataclass


@dataclass
class APIRequest:
    method: str
    path: str
    authenticated_user_id: int
    user_role: str


@dataclass
class AnalysisResult:
    detected: bool
    threats: list
    severity: str