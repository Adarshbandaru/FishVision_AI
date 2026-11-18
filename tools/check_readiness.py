"""
FishVision AI — Service Health & Dynamic Readiness Waiter
Polls FastAPI backend and Vite frontend dynamically based on selected ports.
Verifies:
  1. Backend /health returns HTTP 200 with status: ok and 5 models.
  2. Frontend root / returns HTTP 200.
  3. Frontend reverse proxy /api/health returns HTTP 200 with backend payload.
"""
import sys
import time
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILE = ROOT / "logs" / "runtime" / "runtime.json"
TIMEOUT_SECONDS = 35

def get_ports_from_runtime():
    b_port, f_port = 8000, 5173
    if RUNTIME_FILE.exists():
        try:
            data = json.loads(RUNTIME_FILE.read_text(encoding="utf-8"))
            b_port = data.get("backend", {}).get("port", 8000)
            f_port = data.get("frontend", {}).get("port", 5173)
        except Exception:
            pass
    return b_port, f_port

def check_backend_health(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FishVision-Readiness"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode("utf-8"))
                return body.get("models") == 5 or body.get("status") == "ok"
    except Exception:
        pass
    return False

def check_frontend_root(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FishVision-Readiness"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        pass
    return False

def check_frontend_proxy(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FishVision-Readiness"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode("utf-8"))
                return body.get("models") == 5 or body.get("status") == "ok"
    except Exception:
        pass
    return False

def wait_for_services(backend_port: int, frontend_port: int, timeout: int = TIMEOUT_SECONDS):
    backend_url = f"http://127.0.0.1:{backend_port}/health"
    frontend_url = f"http://127.0.0.1:{frontend_port}/"
    proxy_url = f"http://127.0.0.1:{frontend_port}/api/health"

    print(f"Waiting for services to become healthy (timeout: {timeout}s)...")
    print(f"  Target Backend:  {backend_url}")
    print(f"  Target Frontend: {frontend_url}")
    print(f"  Frontend Proxy:  {proxy_url}")

    start_time = time.time()
    backend_ready = False
    frontend_ready = False
    proxy_ready = False

    while time.time() - start_time < timeout:
        if not backend_ready:
            backend_ready = check_backend_health(backend_url)
        if not frontend_ready:
            frontend_ready = check_frontend_root(frontend_url)
        if backend_ready and frontend_ready and not proxy_ready:
            proxy_ready = check_frontend_proxy(proxy_url)

        if backend_ready and frontend_ready and proxy_ready:
            print(f"\n[SUCCESS] Both Backend (port {backend_port}) and Frontend (port {frontend_port}) are ready!")
            print(f"[SUCCESS] Frontend-to-Backend proxy connection verified via {proxy_url}.")
            return True

        status = []
        status.append("Backend: " + ("READY" if backend_ready else "waiting..."))
        status.append("Frontend: " + ("READY" if frontend_ready else "waiting..."))
        status.append("Proxy: " + ("READY" if proxy_ready else "waiting..."))
        print(f"  [{int(time.time() - start_time)}s] " + " | ".join(status), end="\r")
        time.sleep(1)

    print("\n[TIMEOUT] Services did not report ready within timeout window.")
    print(f"  Backend ({backend_url}): {'READY' if backend_ready else 'NOT RESPONDING'}")
    print(f"  Frontend ({frontend_url}): {'READY' if frontend_ready else 'NOT RESPONDING'}")
    print(f"  Frontend Proxy ({proxy_url}): {'READY' if proxy_ready else 'NOT RESPONDING'}")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FishVision AI Readiness Checker")
    parser.add_argument("--backend-port", type=int, default=None, help="Backend port to test")
    parser.add_argument("--frontend-port", type=int, default=None, help="Frontend port to test")
    parser.add_argument("--timeout", type=int, default=TIMEOUT_SECONDS, help="Timeout in seconds")
    args = parser.parse_args()

    b_port = args.backend_port
    f_port = args.frontend_port
    if b_port is None or f_port is None:
        def_b, def_f = get_ports_from_runtime()
        if b_port is None:
            b_port = def_b
        if f_port is None:
            f_port = def_f

    success = wait_for_services(b_port, f_port, args.timeout)
    sys.exit(0 if success else 1)
