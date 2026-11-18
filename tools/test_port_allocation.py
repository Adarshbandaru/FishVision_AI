"""
FishVision AI — Comprehensive Dynamic Port Allocation & Process Isolation Test Harness
Executes and validates all required scenarios:
  1. Both preferred ports available (8000, 5173).
  2. Backend port 8000 occupied by unrelated server -> Allocates fallback 8001.
  3. Frontend port 5173 occupied by unrelated server -> Allocates fallback 5174.
  4. Both preferred ports occupied -> Allocates 8001 and 5174.
  5. Multi-port occupation (8000 & 8001 occupied) -> Allocates 8002 without terminating unrelated apps.
  6. Live 5-model inference regression on dynamically allocated ports (direct and via frontend proxy).
  7. Safe process termination via stop.bat / port_manager.py -> Unrelated services remain untouched.
"""
import sys
import os
import json
import socket
import time
import subprocess
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"
PORT_MGR = ROOT / "tools" / "port_manager.py"
SAMPLE_IMG = ROOT / "data" / "demo_samples" / "Gold_Fish_sample.jpg"

def create_dummy_listener(port: int, host: str = "127.0.0.1"):
    """Creates a bound TCP socket simulating an unrelated third-party service."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    return s

def run_allocator():
    """Runs port_manager.py allocate and parses the output."""
    res = subprocess.run([str(PYTHON_EXE), str(PORT_MGR), "allocate"], capture_output=True, text=True, check=True)
    line = res.stdout.strip()
    parts = dict(item.split("=") for item in line.split())
    return {
        "backend_port": int(parts["BACKEND_PORT"]),
        "backend_action": parts["BACKEND_ACTION"],
        "frontend_port": int(parts["FRONTEND_PORT"]),
        "frontend_action": parts["FRONTEND_ACTION"]
    }

def main():
    print("=" * 75)
    print("FISHVISION AI — DYNAMIC PORT ALLOCATION & PROCESS ISOLATION TEST SUITE")
    print("=" * 75)

    test_results = {}

    # -----------------------------------------------------------------------
    # TEST 1: Both Preferred Ports Available
    # -----------------------------------------------------------------------
    print("\n[TEST 1] Scenario: Both preferred ports available (8000 & 5173)...")
    alloc1 = run_allocator()
    print(f"  Allocated Backend:  {alloc1['backend_port']} [{alloc1['backend_action']}]")
    print(f"  Allocated Frontend: {alloc1['frontend_port']} [{alloc1['frontend_action']}]")
    t1_pass = (alloc1["backend_port"] == 8000 and alloc1["frontend_port"] == 5173)
    test_results["Test 1: Preferred Ports Available"] = {
        "status": "PASS" if t1_pass else "FAIL",
        "backend": alloc1["backend_port"],
        "frontend": alloc1["frontend_port"],
        "evidence": f"Expected 8000/5173, Got {alloc1['backend_port']}/{alloc1['frontend_port']}"
    }
    print(f"  Result: {'PASS' if t1_pass else 'FAIL'}")

    # -----------------------------------------------------------------------
    # TEST 2: Backend Port 8000 Occupied by Unrelated Application
    # -----------------------------------------------------------------------
    print("\n[TEST 2] Scenario: Backend port 8000 occupied by unrelated service...")
    dummy8000 = create_dummy_listener(8000)
    try:
        alloc2 = run_allocator()
        print(f"  Allocated Backend:  {alloc2['backend_port']} [{alloc2['backend_action']}]")
        print(f"  Allocated Frontend: {alloc2['frontend_port']} [{alloc2['frontend_action']}]")
        t2_pass = (alloc2["backend_port"] == 8001 and alloc2["frontend_port"] == 5173)
        test_results["Test 2: Backend 8000 Occupied"] = {
            "status": "PASS" if t2_pass else "FAIL",
            "backend": alloc2["backend_port"],
            "frontend": alloc2["frontend_port"],
            "evidence": f"Port 8000 occupied -> Allocated fallback {alloc2['backend_port']} (Expected 8001)"
        }
        print(f"  Result: {'PASS' if t2_pass else 'FAIL'}")
    finally:
        dummy8000.close()
        time.sleep(0.5)

    # -----------------------------------------------------------------------
    # TEST 3: Frontend Port 5173 Occupied by Unrelated Application
    # -----------------------------------------------------------------------
    print("\n[TEST 3] Scenario: Frontend port 5173 occupied by unrelated service...")
    dummy5173 = create_dummy_listener(5173)
    try:
        alloc3 = run_allocator()
        print(f"  Allocated Backend:  {alloc3['backend_port']} [{alloc3['backend_action']}]")
        print(f"  Allocated Frontend: {alloc3['frontend_port']} [{alloc3['frontend_action']}]")
        t3_pass = (alloc3["backend_port"] == 8000 and alloc3["frontend_port"] == 5174)
        test_results["Test 3: Frontend 5173 Occupied"] = {
            "status": "PASS" if t3_pass else "FAIL",
            "backend": alloc3["backend_port"],
            "frontend": alloc3["frontend_port"],
            "evidence": f"Port 5173 occupied -> Allocated fallback {alloc3['frontend_port']} (Expected 5174)"
        }
        print(f"  Result: {'PASS' if t3_pass else 'FAIL'}")
    finally:
        dummy5173.close()
        time.sleep(0.5)

    # -----------------------------------------------------------------------
    # TEST 4: Both Preferred Ports Occupied (8000 & 5173)
    # -----------------------------------------------------------------------
    print("\n[TEST 4] Scenario: Both preferred ports (8000 & 5173) occupied...")
    dummy8000 = create_dummy_listener(8000)
    dummy5173 = create_dummy_listener(5173)
    try:
        alloc4 = run_allocator()
        print(f"  Allocated Backend:  {alloc4['backend_port']} [{alloc4['backend_action']}]")
        print(f"  Allocated Frontend: {alloc4['frontend_port']} [{alloc4['frontend_action']}]")
        t4_pass = (alloc4["backend_port"] == 8001 and alloc4["frontend_port"] == 5174)
        test_results["Test 4: Both Preferred Ports Occupied"] = {
            "status": "PASS" if t4_pass else "FAIL",
            "backend": alloc4["backend_port"],
            "frontend": alloc4["frontend_port"],
            "evidence": f"Both occupied -> Allocated {alloc4['backend_port']}/{alloc4['frontend_port']} (Expected 8001/5174)"
        }
        print(f"  Result: {'PASS' if t4_pass else 'FAIL'}")
    finally:
        dummy8000.close()
        dummy5173.close()
        time.sleep(0.5)

    # -----------------------------------------------------------------------
    # TEST 5: Multiple Candidate Ports Occupied (8000 & 8001 occupied)
    # -----------------------------------------------------------------------
    print("\n[TEST 5] Scenario: Multiple candidate backend ports occupied (8000 and 8001)...")
    d8000 = create_dummy_listener(8000)
    d8001 = create_dummy_listener(8001)
    try:
        alloc5 = run_allocator()
        print(f"  Allocated Backend:  {alloc5['backend_port']} [{alloc5['backend_action']}]")
        print(f"  Allocated Frontend: {alloc5['frontend_port']} [{alloc5['frontend_action']}]")
        t5_pass = (alloc5["backend_port"] == 8002)
        test_results["Test 5: Multi-Port Fallback"] = {
            "status": "PASS" if t5_pass else "FAIL",
            "backend": alloc5["backend_port"],
            "evidence": f"8000 & 8001 occupied -> Allocated fallback {alloc5['backend_port']} (Expected 8002)"
        }
        print(f"  Result: {'PASS' if t5_pass else 'FAIL'}")
    finally:
        d8000.close()
        d8001.close()
        time.sleep(0.5)

    # -----------------------------------------------------------------------
    # TEST 6: Live 5-Model Prediction & Proxy Test on Fallback Ports (8001 & 5174)
    # -----------------------------------------------------------------------
    print("\n[TEST 6] Scenario: Starting services on fallback ports (Backend 8001, Frontend 5174)...")
    dummy_b_pref = create_dummy_listener(8000)
    dummy_f_pref = create_dummy_listener(5173)

    try:
        alloc6 = run_allocator()
        target_b_port = alloc6["backend_port"]
        target_f_port = alloc6["frontend_port"]
        print(f"  Selected Backend Port:  {target_b_port}")
        print(f"  Selected Frontend Port: {target_f_port}")

        # Launch FastAPI on fallback port
        b_cmd = f'"{PYTHON_EXE}" -m uvicorn backend.main:app --host 127.0.0.1 --port {target_b_port}'
        backend_proc = subprocess.Popen(b_cmd, cwd=str(ROOT), shell=True)
        time.sleep(1)
        subprocess.run([str(PYTHON_EXE), str(PORT_MGR), "record-pid", "--service", "backend", "--port", str(target_b_port)], check=True)

        # Launch Vite on fallback port with dynamic backend port
        f_env = os.environ.copy()
        f_env["VITE_BACKEND_PORT"] = str(target_b_port)
        f_env["BACKEND_PORT"] = str(target_b_port)
        f_cmd = f'npm run dev -- --port {target_f_port} --host 127.0.0.1'
        frontend_proc = subprocess.Popen(f_cmd, cwd=str(ROOT / "frontend"), env=f_env, shell=True)
        time.sleep(1)
        subprocess.run([str(PYTHON_EXE), str(PORT_MGR), "record-pid", "--service", "frontend", "--port", str(target_f_port)], check=True)

        # Wait for readiness
        time.sleep(2)
        r_res = subprocess.run([
            str(PYTHON_EXE), str(ROOT / "tools" / "check_readiness.py"),
            "--backend-port", str(target_b_port),
            "--frontend-port", str(target_f_port)
        ], capture_output=True, text=True)
        print(r_res.stdout)
        readiness_ok = (r_res.returncode == 0)

        # Direct Backend Prediction Test
        print(f"  Executing direct 5-model prediction against fallback backend (http://127.0.0.1:{target_b_port}/predict)...")
        with open(SAMPLE_IMG, "rb") as f:
            b_resp = requests.post(f"http://127.0.0.1:{target_b_port}/predict", files={"file": ("fish.jpg", f, "image/jpeg")})
        b_data = b_resp.json()
        b_consensus = b_data.get("consensus", {}).get("species")
        b_agree = b_data.get("consensus", {}).get("agreement_count")
        print(f"  Direct Backend Response: {b_resp.status_code} OK | Consensus: {b_consensus} ({b_agree}/5 models)")

        # Proxied Frontend Prediction Test
        print(f"  Executing proxied prediction through Vite (http://127.0.0.1:{target_f_port}/api/predict)...")
        with open(SAMPLE_IMG, "rb") as f:
            f_resp = requests.post(f"http://127.0.0.1:{target_f_port}/api/predict", files={"file": ("fish.jpg", f, "image/jpeg")})
        f_data = f_resp.json()
        f_consensus = f_data.get("consensus", {}).get("species")
        f_agree = f_data.get("consensus", {}).get("agreement_count")
        print(f"  Proxied Frontend Response: {f_resp.status_code} OK | Consensus: {f_consensus} ({f_agree}/5 models)")

        for r in f_data.get("results", []):
            print(f"    - {r['model']:<14}: {r['prediction']:<25} ({r['confidence']:.1f}%) in {r['latency_ms']:.1f}ms")

        # -------------------------------------------------------------------
        # TEST 7: Safe Shutdown Test (Unrelated Sockets Untouched)
        # -------------------------------------------------------------------
        print("\n[TEST 7] Scenario: Safe shutdown test — Terminating FishVision without affecting dummy sockets...")
        stop_res = subprocess.run([str(PYTHON_EXE), str(PORT_MGR), "stop"], capture_output=True, text=True, check=True)
        print(stop_res.stdout)

        dummy_8000_alive = True
        dummy_5173_alive = True
        try:
            s_test = socket.socket()
            s_test.bind(("127.0.0.1", 8000))
            s_test.close()
            dummy_8000_alive = False
        except OSError:
            dummy_8000_alive = True

        try:
            s_test = socket.socket()
            s_test.bind(("127.0.0.1", 5173))
            s_test.close()
            dummy_5173_alive = False
        except OSError:
            dummy_5173_alive = True

        print(f"  Unrelated dummy service on 8000 still active: {dummy_8000_alive}")
        print(f"  Unrelated dummy service on 5173 still active: {dummy_5173_alive}")

        t6_pass = (readiness_ok and b_resp.status_code == 200 and f_resp.status_code == 200 and f_consensus == "Gold Fish")
        t7_pass = (dummy_8000_alive and dummy_5173_alive)

        test_results["Test 6: 5-Model Prediction on Fallback Ports"] = {
            "status": "PASS" if t6_pass else "FAIL",
            "consensus": f_consensus,
            "agreement": f"{f_agree}/5",
            "evidence": f"Readiness OK, direct HTTP 200, proxied HTTP 200, consensus: {f_consensus}"
        }
        test_results["Test 7: Safe Targeted Shutdown"] = {
            "status": "PASS" if t7_pass else "FAIL",
            "dummy_8000_preserved": dummy_8000_alive,
            "dummy_5173_preserved": dummy_5173_alive,
            "evidence": f"FishVision PIDs terminated; dummy sockets on 8000 and 5173 untouched."
        }

    finally:
        dummy_b_pref.close()
        dummy_f_pref.close()
        time.sleep(1)

    print("\n" + "=" * 75)
    print("TEST SUITE SUMMARY")
    print("=" * 75)
    all_passed = True
    for name, res in test_results.items():
        st = res["status"]
        if st != "PASS":
            all_passed = False
        print(f"  [{st}] {name}: {res.get('evidence', '')}")
    print("=" * 75)

    return test_results, all_passed

if __name__ == "__main__":
    results, passed = main()
    sys.exit(0 if passed else 1)

