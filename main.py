from dataclasses import asdict
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pydantic import BaseModel
from app.rate_limiter import RequestRateLimiter
from runtime.analyzer import analyze_request
from runtime.models import APIRequest
from runtime.analyzer import (
    analyze_shadow_apis
)

app = FastAPI(
    title="API-Sentinel",
    description="Runtime BOLA, BFLA, and API security analysis engine",
    version="0.1.0",
)


rate_limiter = RequestRateLimiter(
    max_requests=20,
    window_seconds=10,
)


class AnalyzeRequest(BaseModel):
    method: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)
    authenticated_user_id: int
    user_role: str = Field(..., min_length=1)
    client_id: str = Field(default="default-client", min_length=1)


@app.get("/")
def root():
    return {
        "service": "API-Sentinel",
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "engine": "API-Sentinel Runtime Security Engine",
    }


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    rate_limit = rate_limiter.check(
        user_id=request.client_id,
        endpoint=request.path,
    )

    if not rate_limit.allowed:
        return {
            "allowed": False,
            "blocked": True,
            "block_reason": rate_limit.reason,
            "rate_limit": asdict(rate_limit),
            "analysis": None,
        }

    api_request = APIRequest(
        method=request.method,
        path=request.path,
        authenticated_user_id=request.authenticated_user_id,
        user_role=request.user_role,
    )

    result = analyze_request(api_request)

    return {
        "allowed": not result.detected,
        "blocked": False,
        "rate_limit": asdict(rate_limit),
        "analysis": asdict(result),
    }
class ShadowScanRequest(
    BaseModel
):
    spec_path: str
    observed_endpoints: list

@app.post(
    "/shadow-scan"
)
def shadow_scan(
    request: ShadowScanRequest
):

    result = analyze_shadow_apis(
        request.spec_path,
        request.observed_endpoints
    )

    return result