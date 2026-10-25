"""Performance smoke test (non-functional check).

Starts the API on a local port, fires concurrent requests at GET /courses
and POST /register, then reports latency percentiles.
Pass criteria: 0 errors and p95 latency < 200 ms.

Run:  python -m tests.perf_smoke
"""
import json
import logging
import statistics
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from werkzeug.serving import make_server

from app.api import create_app

HOST, PORT = "127.0.0.1", 5055
TOTAL_REQUESTS = 500
CONCURRENCY = 20
P95_LIMIT_MS = 200


def one_request(i):
    start = time.perf_counter()
    try:
        if i % 5 == 0:  # 20% writes
            body = json.dumps({"student_id": "S1001", "course_code": "HIST100"}).encode()
            req = urllib.request.Request(
                f"http://{HOST}:{PORT}/register", data=body,
                headers={"Content-Type": "application/json"}, method="POST")
        else:
            req = urllib.request.Request(f"http://{HOST}:{PORT}/courses")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310 - local URL only
                status = resp.status
        except urllib.error.HTTPError as e:
            status = e.code  # 409 duplicate is an expected business answer, not an error
        ok = status in (200, 201, 409)
    except Exception:
        ok = False
    return (time.perf_counter() - start) * 1000, ok


def main():
    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # keep output readable
    server = make_server(HOST, PORT, create_app(), threaded=True)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)

    wall = time.perf_counter()
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        results = list(pool.map(one_request, range(TOTAL_REQUESTS)))
    wall = time.perf_counter() - wall
    server.shutdown()

    latencies = sorted(r[0] for r in results)
    errors = sum(1 for r in results if not r[1])
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    summary = {
        "requests": TOTAL_REQUESTS,
        "concurrency": CONCURRENCY,
        "errors": errors,
        "throughput_rps": round(TOTAL_REQUESTS / wall, 1),
        "p50_ms": round(p50, 1),
        "p95_ms": round(p95, 1),
        "max_ms": round(latencies[-1], 1),
        "p95_limit_ms": P95_LIMIT_MS,
        "passed": errors == 0 and p95 < P95_LIMIT_MS,
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
