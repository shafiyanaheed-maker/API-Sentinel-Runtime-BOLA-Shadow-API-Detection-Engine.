# API-Sentinel — Enforcement, Rate Limiting & Attack Simulation

Owner: Anshika

Covers: request validation, authorization enforcement (BOLA/BFLA),
rate limiting, attack simulation, and detection-accuracy validation
for the API-Sentinel project.

## Setup
pip install -r requirements.txt

## Progress

- [x] Sliding-window rate limiter (`app/rate_limiter.py`) — limits requests
      per user per endpoint within a time window. Tested in `tests/test_rate_limiter.py`.
- [x] Business-flow limiter (object-scan detection) — counts distinct object
      IDs per user per endpoint pattern. Tested in `tests/test_rate_limiter.py`.
- [x] Authorization enforcement (BOLA + BFLA) — object-level ownership
      checks and role-based function-level checks, with default-deny
      for unregistered endpoints. Tested in `tests/test_authorization.py`.
- [x] Blocking middleware — enforces all four checks (volume rate limit,
      business-flow rate limit, BFLA, BOLA) in sequence on every request.
      Demo app at `app/main.py` verified with end-to-end curl tests.
- [x] Attack simulation scripts — BOLA, BFLA, and rate-limit/slow-scan
      attacks, plus a combined runner. Verified against a live server.
- [x] Detection-accuracy validation — labelled legitimate + attack traffic,
      confusion matrix, precision/recall/F1. Achieved 1.0 precision,
      1.0 recall, 0.0 false-positive rate on the test set.