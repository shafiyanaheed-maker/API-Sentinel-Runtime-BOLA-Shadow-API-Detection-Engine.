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
- [ ] Authorization enforcement (BOLA/BFLA)
- [ ] Blocking middleware
- [ ] Attack simulation scripts
- [ ] Detection-accuracy validation