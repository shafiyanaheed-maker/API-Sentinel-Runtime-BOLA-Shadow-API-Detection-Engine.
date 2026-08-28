from detection_engine.bfla.detector import detect_bfla
from detection_engine.bola.detector import detect_bola

from .models import APIRequest, AnalysisResult


SEVERITY_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def analyze_request(request: APIRequest) -> AnalysisResult:
    bola_result = detect_bola(
        method=request.method,
        path=request.path,
        authenticated_user_id=request.authenticated_user_id,
    )

    bfla_result = detect_bfla(
        method=request.method,
        path=request.path,
        user_role=request.user_role,
    )

    threats = []

    if bola_result["detected"]:
        threats.append(bola_result)

    if bfla_result["detected"]:
        threats.append(bfla_result)

    severity = "LOW"

    for threat in threats:
        threat_severity = threat.get("severity", "LOW")

        if (
            SEVERITY_LEVELS.get(threat_severity, 0)
            > SEVERITY_LEVELS.get(severity, 0)
        ):
            severity = threat_severity

    return AnalysisResult(
        detected=bool(threats),
        threats=threats,
        severity=severity,
    )