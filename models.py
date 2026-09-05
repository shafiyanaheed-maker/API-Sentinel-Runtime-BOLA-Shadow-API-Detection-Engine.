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

@dataclass
class ShadowAPIResult:
    shadow_apis: list
    zombie_apis: list
    count_shadow: int
    count_zombie: int    