"""
API Latency Benchmark
======================
5-minute benchmark hitting all key Django endpoints.
Starts the Django dev server, runs benchmarks, and stops it.

Usage:
    python scripts/benchmark_api.py
    python scripts/benchmark_api.py --duration 300 --base-url http://localhost:8000
"""

import os
import sys
import json
import time
import signal
import logging
import argparse
import subprocess
import statistics
from pathlib import Path
from typing import Dict, List, Any

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
RESULTS_DIR = BACKEND_DIR / "evaluation_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_BASE = "http://127.0.0.1:8000"


def count_endpoints():
    """Count total URL patterns from Django URL configs."""
    sys.path.insert(0, str(BACKEND_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KrishiSaarthi.settings")

    try:
        import django
        django.setup()
        from django.urls import get_resolver
        resolver = get_resolver()

        def _count(resolver, prefix=""):
            count = 0
            patterns = []
            for pattern in resolver.url_patterns:
                full = prefix + str(pattern.pattern)
                if hasattr(pattern, "url_patterns"):
                    c, p = _count(pattern, full)
                    count += c
                    patterns.extend(p)
                else:
                    count += 1
                    patterns.append(full)
            return count, patterns

        total, all_patterns = _count(resolver)
        return total, all_patterns
    except Exception as e:
        logger.warning("Could not count endpoints: %s", e)
        return 0, []


def start_django_server(port=8000):
    """Start Django dev server as subprocess."""
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "KrishiSaarthi.settings"
    proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    # Wait for server startup
    for _ in range(30):
        time.sleep(1)
        try:
            r = requests.get(f"http://127.0.0.1:{port}/api/v1/field/data", timeout=2)
            if r.status_code in (200, 401, 403):
                logger.info("Django server started on port %d", port)
                return proc
        except requests.ConnectionError:
            continue

    logger.error("Django server failed to start")
    proc.kill()
    return None


def stop_server(proc):
    """Stop Django dev server."""
    if proc:
        try:
            if sys.platform == "win32":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        logger.info("Django server stopped")


def register_and_login(base_url: str) -> str:
    """Register a test user and get auth token."""
    import random
    import string
    suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    username = f"bench_{suffix}"
    password = "BenchTest123!"

    # Try registration
    try:
        r = requests.post(f"{base_url}/api/v1/auth/register", json={
            "username": username,
            "password": password,
            "email": f"{username}@test.com",
        }, timeout=10)
    except Exception:
        pass

    # Try login (knox)
    for login_url in [
        f"{base_url}/api/v1/auth/login",
        f"{base_url}/api/v1/auth/signin",
    ]:
        try:
            r = requests.post(login_url, json={
                "username": username,
                "password": password,
            }, timeout=10)
            if r.status_code == 200:
                data = r.json()
                token = data.get("token") or data.get("key") or data.get("access")
                if token:
                    logger.info("Authenticated as %s", username)
                    return token
        except Exception:
            continue

    logger.warning("Could not authenticate. Benchmarks will run without auth.")
    return ""


def benchmark_endpoint(url: str, headers: dict, method="GET", iterations=10, payload=None) -> Dict[str, Any]:
    """Benchmark a single endpoint."""
    times = []
    statuses = []
    errors = 0

    for _ in range(iterations):
        try:
            t0 = time.perf_counter()
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            else:
                r = requests.post(url, json=payload, headers=headers, timeout=30)
            elapsed = time.perf_counter() - t0

            times.append(elapsed * 1000)
            statuses.append(r.status_code)
        except Exception as e:
            errors += 1
            times.append(30000)  # timeout penalty
            statuses.append(0)

    return {
        "avg_ms": round(statistics.mean(times), 1),
        "min_ms": round(min(times), 1),
        "max_ms": round(max(times), 1),
        "median_ms": round(statistics.median(times), 1),
        "p95_ms": round(sorted(times)[int(0.95 * len(times))], 1) if len(times) > 1 else round(times[0], 1),
        "std_ms": round(statistics.stdev(times), 1) if len(times) > 1 else 0,
        "status_codes": list(set(statuses)),
        "error_count": errors,
        "iterations": len(times),
    }


def run_benchmarks(base_url: str, token: str, duration_seconds: int = 300):
    """Run full API benchmark suite."""
    headers = {}
    if token:
        headers["Authorization"] = f"Token {token}"

    # Define endpoints to benchmark
    endpoints = [
        # Field endpoints (with EE calls)
        {"name": "Health Score", "path": "/api/v1/field/healthscore", "ee": True},
        {"name": "Pest Prediction", "path": "/api/v1/field/pestpredict", "ee": True},
        {"name": "AWD Report", "path": "/api/v1/field/awd", "ee": True},
        {"name": "Carbon Credit", "path": "/api/v1/field/cc", "ee": True},
        {"name": "EE Analysis", "path": "/api/v1/field/ee", "ee": True},
        {"name": "Yield Prediction", "path": "/api/v1/field/yield-prediction?field_id=1", "ee": True},
        {"name": "Weather", "path": "/api/v1/field/weather", "ee": False},
        # Field data (no EE)
        {"name": "Field Data List", "path": "/api/v1/field/data", "ee": False},
        {"name": "Field Logs", "path": "/api/v1/field/logs", "ee": False},
        {"name": "Field Alerts", "path": "/api/v1/field/alerts", "ee": False},
        {"name": "Soil Advice", "path": "/api/v1/field/soil-advice", "ee": False},
        {"name": "Irrigation Schedule", "path": "/api/v1/field/irrigation-schedule", "ee": False},
        # Finance endpoints (no EE)
        {"name": "Cost List", "path": "/api/v1/finance/costs", "ee": False},
        {"name": "Cost Summary", "path": "/api/v1/finance/costs/summary", "ee": False},
        {"name": "Revenue List", "path": "/api/v1/finance/revenue", "ee": False},
        {"name": "P&L Dashboard", "path": "/api/v1/finance/pnl", "ee": False},
        {"name": "Seasons", "path": "/api/v1/finance/seasons", "ee": False},
        {"name": "Schemes", "path": "/api/v1/finance/schemes", "ee": False},
        {"name": "Insurance Claims", "path": "/api/v1/finance/insurance", "ee": False},
        {"name": "Market Prices", "path": "/api/v1/finance/market-prices", "ee": False},
        {"name": "Price Forecast", "path": "/api/v1/finance/price-forecast", "ee": False},
        {"name": "Transactions", "path": "/api/v1/finance/transactions", "ee": False},
    ]

    results = {}
    start_time = time.time()
    iteration = 0

    logger.info("Starting %d-second benchmark across %d endpoints...", duration_seconds, len(endpoints))

    while (time.time() - start_time) < duration_seconds:
        iteration += 1
        logger.info("--- Benchmark round %d (%.0fs elapsed) ---", iteration, time.time() - start_time)

        for ep in endpoints:
            if (time.time() - start_time) >= duration_seconds:
                break

            url = f"{base_url}{ep['path']}"
            name = ep["name"]

            if name not in results:
                results[name] = {"times": [], "statuses": [], "errors": 0, "ee": ep["ee"]}

            try:
                t0 = time.perf_counter()
                r = requests.get(url, headers=headers, timeout=60)
                elapsed = (time.perf_counter() - t0) * 1000

                results[name]["times"].append(elapsed)
                results[name]["statuses"].append(r.status_code)

                logger.info("  %s: %d (%.0fms)", name, r.status_code, elapsed)
            except Exception as e:
                results[name]["errors"] += 1
                results[name]["times"].append(60000)
                logger.warning("  %s: ERROR (%s)", name, e)

    # Compute final stats
    final_results = {}
    for name, data in results.items():
        times = [t for t in data["times"] if t < 60000]  # exclude timeouts
        if not times:
            times = [0]

        final_results[name] = {
            "avg_ms": round(statistics.mean(times), 1),
            "min_ms": round(min(times), 1),
            "max_ms": round(max(times), 1),
            "median_ms": round(statistics.median(times), 1),
            "p95_ms": round(sorted(times)[int(0.95 * len(times))], 1) if len(times) > 1 else round(times[0], 1),
            "requests": len(data["times"]),
            "errors": data["errors"],
            "has_ee_calls": data["ee"],
            "status_codes": sorted(set(data["statuses"])),
        }

    total_elapsed = time.time() - start_time
    total_requests = sum(r["requests"] for r in final_results.values())

    return {
        "benchmark_duration_seconds": round(total_elapsed, 1),
        "total_requests": total_requests,
        "requests_per_second": round(total_requests / total_elapsed, 2),
        "rounds": iteration,
        "endpoints": final_results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--duration", type=int, default=300, help="Benchmark duration in seconds")
    parser.add_argument("--no-server", action="store_true", help="Don't start Django server")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Count endpoints
    total_endpoints, all_patterns = count_endpoints()
    logger.info("Total registered URL endpoints: %d", total_endpoints)

    # Start server
    server_proc = None
    if not args.no_server:
        logger.info("Starting Django dev server...")
        server_proc = start_django_server(args.port)
        if not server_proc:
            logger.error("Failed to start server")
            sys.exit(1)
    else:
        logger.info("Using existing server at %s", args.base_url)

    try:
        # Auth
        token = register_and_login(args.base_url)

        # Run benchmarks
        results = run_benchmarks(args.base_url, token, args.duration)
        results["total_registered_endpoints"] = total_endpoints
        results["endpoint_list_sample"] = all_patterns[:50]

        # Save
        output_path = RESULTS_DIR / "api_benchmarks.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info("Results saved to %s", output_path)

        # Print summary
        print("\n" + "=" * 70)
        print("API BENCHMARK RESULTS")
        print("=" * 70)
        print(f"Duration:           {results['benchmark_duration_seconds']}s")
        print(f"Total Requests:     {results['total_requests']}")
        print(f"Req/sec:            {results['requests_per_second']}")
        print(f"Total Endpoints:    {total_endpoints}")
        print()
        print(f"{'Endpoint':<25} {'Avg':>8} {'Med':>8} {'P95':>8} {'Min':>8} {'Max':>8} {'N':>5} {'EE':>4}")
        print("-" * 78)
        for name, data in sorted(results["endpoints"].items(), key=lambda x: x[1]["avg_ms"], reverse=True):
            ee = "Yes" if data["has_ee_calls"] else "No"
            print(f"{name:<25} {data['avg_ms']:>7.0f}ms {data['median_ms']:>7.0f}ms {data['p95_ms']:>7.0f}ms "
                  f"{data['min_ms']:>7.0f}ms {data['max_ms']:>7.0f}ms {data['requests']:>5} {ee:>4}")
        print("=" * 70)

    finally:
        stop_server(server_proc)


if __name__ == "__main__":
    main()
