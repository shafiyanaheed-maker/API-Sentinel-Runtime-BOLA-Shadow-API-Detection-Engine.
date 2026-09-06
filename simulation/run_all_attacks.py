"""
run_all_attacks.py

Runs the full attack simulation suite against a live demo server and
prints a combined summary. Use this for project demos and reviews.

Usage:
    uvicorn app.main:app --port 8000   (in one terminal)
    python -m simulation.run_all_attacks   (in another terminal)
"""

from simulation.bola_attack import run as run_bola
from simulation.bfla_attack import run as run_bfla
from simulation.rate_limit_attack import burst_flood, slow_scan


def main():
    print("#" * 60)
    print("API-Sentinel Enforcement - Full Attack Simulation Suite")
    print("#" * 60)

    bola_results = run_bola()
    bfla_results = run_bfla()
    flood_blocked = burst_flood()
    scan_blocked = slow_scan()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    bola_blocked = sum(1 for _, _, b in bola_results if b)
    bfla_blocked = sum(1 for _, _, b in bfla_results if b)
    print(f"BOLA cross-owner reads blocked      : {bola_blocked}/{len(bola_results)}")
    print(f"BFLA admin-endpoint attempts blocked : {bfla_blocked}/{len(bfla_results)}")
    print(f"Burst-flood requests blocked         : {flood_blocked}/30")
    print(f"Slow-scan requests blocked           : {scan_blocked}/8")


if __name__ == "__main__":
    main()