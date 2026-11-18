"""
FishVision AI — Dynamic Port Allocation and Process Management Engine
Handles:
  1. Discovery of free candidate ports for Backend (8000-8004) and Frontend (5173-5177).
  2. Health-checking existing instances before reuse.
  3. Non-destructive port skipping when candidate ports are held by unrelated applications.
  4. Precise runtime state recording (PIDs, ports, URLs) in logs/runtime/runtime.json.
  5. Isolated, safe shutdown targeting ONLY FishVision PIDs.
"""
import sys
import os
import json
import socket
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "logs" / "runtime"
RUNTIME_FILE = RUNTIME_DIR / "runtime.json"

BACKEND_CANDIDATE_PORTS = [8000, 8001, 8002, 8003, 8004]
FRONTEND_CANDIDATE_PORTS = [5173, 5174, 5175, 5176, 5177]

def ensure_runtime_dir():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

def is_socket_bound(port: int, host: str = "127.0.0.1") -> bool:
    """Returns True if the port is currently bound/listening, False if free."""
    # Test 1: Attempt to bind
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
        s.close()
    except OSError:
        return True

    # Test 2: Attempt to connect
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.settimeout(0.3)
    try:
        res = c.connect_ex((host, port))
        c.close()
        if res == 0:
            return True
    except Exception:
        pass

    return False

def check_fishvision_backend_health(port: int) -> bool:
    """Verifies if an occupied port is actively hosting a healthy FishVision FastAPI backend."""
    url = f"http://127.0.0.1:{port}/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FishVision-PortManager"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("models") == 5 or data.get("status") == "ok"
    except Exception:
        pass
    return False

def check_fishvision_frontend_health(port: int, expected_backend_port: int = None) -> bool:
    """Verifies if an occupied port is actively hosting a FishVision Vite frontend."""
    # Check root HTML container
    url_root = f"http://127.0.0.1:{port}/"
    try:
        req = urllib.request.Request(url_root, headers={"User-Agent": "FishVision-PortManager"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status != 200:
                return False
    except Exception:
        return False

    # Check proxied /api/health endpoint
    url_api = f"http://127.0.0.1:{port}/api/health"
    try:
        req = urllib.request.Request(url_api, headers={"User-Agent": "FishVision-PortManager"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("models") == 5 or data.get("status") == "ok"
    except Exception:
        return False

    return True

def allocate_ports():
    """
    Selects the first available or healthy reusable port for backend and frontend.
    Returns:
      (backend_port, backend_action, frontend_port, frontend_action)
    """
    ensure_runtime_dir()

    # 1. Allocate Backend Port
    selected_backend = None
    backend_action = None
    backend_diagnostics = []

    for p in BACKEND_CANDIDATE_PORTS:
        occupied = is_socket_bound(p)
        if not occupied:
            selected_backend = p
            backend_action = "START"
            backend_diagnostics.append(f"Port {p}: AVAILABLE (Selected for new backend)")
            break
        else:
            # Check if it's an existing healthy FishVision backend
            if check_fishvision_backend_health(p):
                selected_backend = p
                backend_action = "REUSE"
                backend_diagnostics.append(f"Port {p}: OCCUPIED by active FishVision backend (Reusing)")
                break
            else:
                backend_diagnostics.append(f"Port {p}: OCCUPIED by unrelated service/process (Skipped)")

    if selected_backend is None:
        sys.stderr.write("[ERROR] All candidate backend ports (8000, 8001, 8002, 8003, 8004) are occupied.\n")
        for d in backend_diagnostics:
            sys.stderr.write(f"  - {d}\n")
        sys.exit(1)

    # 2. Allocate Frontend Port
    selected_frontend = None
    frontend_action = None
    frontend_diagnostics = []

    for p in FRONTEND_CANDIDATE_PORTS:
        occupied = is_socket_bound(p)
        if not occupied:
            selected_frontend = p
            frontend_action = "START"
            frontend_diagnostics.append(f"Port {p}: AVAILABLE (Selected for new frontend)")
            break
        else:
            # Check if it's an existing healthy FishVision frontend proxying to selected backend
            if check_fishvision_frontend_health(p, selected_backend):
                selected_frontend = p
                frontend_action = "REUSE"
                frontend_diagnostics.append(f"Port {p}: OCCUPIED by active FishVision frontend (Reusing)")
                break
            else:
                frontend_diagnostics.append(f"Port {p}: OCCUPIED by unrelated service/process (Skipped)")

    if selected_frontend is None:
        sys.stderr.write("[ERROR] All candidate frontend ports (5173, 5174, 5175, 5176, 5177) are occupied.\n")
        for d in frontend_diagnostics:
            sys.stderr.write(f"  - {d}\n")
        sys.exit(1)

    # Save initial runtime configuration
    runtime_data = {
        "backend": {
            "port": selected_backend,
            "action": backend_action,
            "pid": None,
            "url": f"http://127.0.0.1:{selected_backend}"
        },
        "frontend": {
            "port": selected_frontend,
            "action": frontend_action,
            "pid": None,
            "url": f"http://127.0.0.1:{selected_frontend}"
        },
        "allocated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "diagnostics": {
            "backend": backend_diagnostics,
            "frontend": frontend_diagnostics
        }
    }
    RUNTIME_FILE.write_text(json.dumps(runtime_data, indent=2), encoding="utf-8")

    # Write set_ports.bat for seamless, quote-safe consumption by run.bat
    set_ports_bat = RUNTIME_DIR / "set_ports.bat"
    set_ports_content = (
        f'@echo off\r\n'
        f'set "BACKEND_PORT={selected_backend}"\r\n'
        f'set "BACKEND_ACTION={backend_action}"\r\n'
        f'set "FRONTEND_PORT={selected_frontend}"\r\n'
        f'set "FRONTEND_ACTION={frontend_action}"\r\n'
    )
    set_ports_bat.write_text(set_ports_content, encoding="utf-8")

    # Output machine-parseable string for CLI/logging
    print(f"BACKEND_PORT={selected_backend} BACKEND_ACTION={backend_action} FRONTEND_PORT={selected_frontend} FRONTEND_ACTION={frontend_action}")
    return selected_backend, backend_action, selected_frontend, frontend_action

def get_pid_listening_on_port(port: int) -> int:
    """Finds the process ID listening on a given TCP port using netstat."""
    try:
        cmd = 'netstat -aon -p TCP'
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        target = f":{port}"
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[0].upper() == "TCP":
                local_addr = parts[1]
                state = parts[3]
                pid_str = parts[4]
                if (local_addr.endswith(target) or local_addr.endswith(f":{port}")) and state.upper() == "LISTENING":
                    try:
                        pid = int(pid_str)
                        if pid > 0:
                            return pid
                    except ValueError:
                        pass
    except Exception:
        pass
    return None

def record_pid(service_name: str, port: int, wait_seconds: int = 25):
    """Waits for service to listen on port and records the exact PID."""
    ensure_runtime_dir()
    start = time.time()
    pid = None

    while time.time() - start < wait_seconds:
        pid = get_pid_listening_on_port(port)
        if pid:
            break
        time.sleep(0.5)

    if not pid:
        sys.stderr.write(f"[WARNING] Could not resolve listening PID for {service_name} on port {port} within {wait_seconds}s.\n")
        return None

    # Write service PID file
    pid_file = RUNTIME_DIR / f"{service_name}.pid"
    pid_file.write_text(str(pid), encoding="utf-8")

    # Update runtime.json
    try:
        data = {}
        if RUNTIME_FILE.exists():
            data = json.loads(RUNTIME_FILE.read_text(encoding="utf-8"))
        if service_name not in data:
            data[service_name] = {}
        data[service_name]["port"] = port
        data[service_name]["pid"] = pid
        data[service_name]["status"] = "running"
        data[service_name]["pid_recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        RUNTIME_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"[WARNING] Failed updating runtime.json with PID {pid}: {e}\n")

    print(f"Recorded {service_name} PID: {pid} on port {port}")
    return pid

def is_pid_alive(pid: int) -> bool:
    """Checks if a process ID is currently running on Windows."""
    try:
        out = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /NH', shell=True, text=True, stderr=subprocess.DEVNULL)
        return str(pid) in out
    except Exception:
        return False

def get_process_image_name(pid: int) -> str:
    """Returns the executable image name of a given PID."""
    try:
        out = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /NH', shell=True, text=True, stderr=subprocess.DEVNULL)
        parts = out.strip().split()
        if parts:
            return parts[0].lower()
    except Exception:
        pass
    return ""

def stop_services():
    """
    Terminates ONLY the processes started by this FishVision instance
    using the tracked PIDs in logs/runtime/.
    Guarantees no unrelated processes are affected.
    """
    ensure_runtime_dir()
    stopped_count = 0
    terminated_details = []

    # Read runtime.json
    runtime_data = {}
    if RUNTIME_FILE.exists():
        try:
            runtime_data = json.loads(RUNTIME_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    services = ["backend", "frontend"]
    pids_to_kill = {}

    for s in services:
        pid = None
        pid_file = RUNTIME_DIR / f"{s}.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
            except Exception:
                pass
        if not pid and s in runtime_data and runtime_data[s].get("pid"):
            pid = runtime_data[s]["pid"]

        if pid:
            pids_to_kill[s] = pid

    # If PID files were missing, safely check the ports recorded in runtime.json
    for s in services:
        if s not in pids_to_kill and s in runtime_data:
            p = runtime_data[s].get("port")
            if p:
                listening_pid = get_pid_listening_on_port(p)
                if listening_pid:
                    img_name = get_process_image_name(listening_pid)
                    # Verify process type before targeting
                    if s == "backend" and ("python" in img_name or "uvicorn" in img_name):
                        pids_to_kill[s] = listening_pid
                    elif s == "frontend" and ("node" in img_name or "cmd" in img_name):
                        pids_to_kill[s] = listening_pid

    for s, pid in pids_to_kill.items():
        if is_pid_alive(pid):
            img = get_process_image_name(pid)
            print(f"  Terminating {s} service [PID: {pid}, Image: {img}]...")
            try:
                subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                stopped_count += 1
                terminated_details.append(f"{s} (PID {pid})")
            except Exception as e:
                print(f"  Failed terminating {s} PID {pid}: {e}")
        else:
            print(f"  Service {s} [PID: {pid}] was already stopped.")

    # Clean up PID files and runtime state
    for s in services:
        pid_file = RUNTIME_DIR / f"{s}.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
            except Exception:
                pass

    if RUNTIME_FILE.exists():
        try:
            if runtime_data:
                for s in services:
                    if s in runtime_data:
                        runtime_data[s]["status"] = "stopped"
                        runtime_data[s]["pid"] = None
                runtime_data["stopped_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                RUNTIME_FILE.write_text(json.dumps(runtime_data, indent=2), encoding="utf-8")
        except Exception:
            pass

    print()
    if stopped_count > 0:
        print(f"[SUCCESS] {stopped_count} FishVision AI service process(es) terminated: {', '.join(terminated_details)}")
        print("Ports have been released.")
    else:
        print("[INFO] No active FishVision AI services were running [already stopped].")

    return stopped_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: port_manager.py [allocate | record-pid --service <name> --port <port> | stop]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "allocate":
        allocate_ports()
    elif cmd == "record-pid":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--service", required=True, choices=["backend", "frontend"])
        parser.add_argument("--port", type=int, required=True)
        parser.add_argument("--wait", type=int, default=25)
        args = parser.parse_args(sys.argv[2:])
        record_pid(args.service, args.port, args.wait)
    elif cmd == "stop":
        stop_services()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
