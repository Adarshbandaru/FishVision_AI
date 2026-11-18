# FishVision AI — Dynamic Port Allocation & Process Isolation Report

**Platform Version:** 2.4  
**Date of Audit:** November 11, 2026  
**Auditor:** Senior Windows DevOps & Full-Stack Deployment Specialist  
**Project Root:** `C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App`  

---

## Executive Summary

FishVision AI has been upgraded with **fully dynamic, non-destructive port allocation** and **isolated process tracking** for both backend (FastAPI) and frontend (React + Vite) services on Windows.

If preferred ports are already occupied by another application, the system automatically detects the conflict, leaves the external application running unharmed, and seamlessly selects the next available port from a designated candidate pool. The Vite reverse proxy dynamically targets the allocated backend port, ensuring that 100% of API endpoints, computer vision pipelines, and 5-model neural ensemble predictions reach the correct backend instance without hardcoded ports.

---

## 1. Port Candidate Specifications

| Service | Preferred Port | Fallback Candidate Pool | Bind Interface | Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI ML Backend** | `8000` | `8001`, `8002`, `8003`, `8004` | `127.0.0.1` | HTTP / REST |
| **React + Vite Frontend** | `5173` | `5174`, `5175`, `5176`, `5177` | `127.0.0.1` | HTTP / SPA |

---

## 2. Dynamic Port Allocation Architecture

### 2.1 Non-Destructive Port Discovery (`tools/port_manager.py`)
1. **Socket Probing:** Each candidate port is tested for availability via dual socket checks (`socket.bind` and `connect_ex`).
2. **FishVision Instance Reuse:** If a candidate port is occupied, the allocator performs a health probe (`GET http://127.0.0.1:<port>/health`). If the response payload contains `"status": "ok"` and `"models": 5`, it recognizes an existing healthy FishVision backend and marks it for reuse (`REUSE`), rather than launching a redundant process.
3. **Unrelated Application Protection:** If an occupied port belongs to an unrelated service (or returns non-FishVision data), the port manager leaves it completely untouched and continues searching the candidate list.
4. **Exhaustion Guard:** If all 5 candidate ports are occupied, the launcher aborts cleanly with an explicit error message and exits without starting empty terminal windows.

### 2.2 Dynamic Frontend Proxy Configuration (`frontend/vite.config.ts`)
The Vite configuration dynamically resolves the backend target using a 3-tier hierarchy:
1. `process.env.VITE_BACKEND_PORT` / `process.env.BACKEND_PORT`
2. `logs/runtime/runtime.json`
3. Fallback default (`8000`)

```ts
const backendTarget = `http://127.0.0.1:${backendPort}`;
// Automatically updates both /api and /samples/image reverse proxy routes
```
All frontend requests in `frontend/src/services/api.ts` use relative `/api/*` and `/samples/image/*` URLs. Vite reverse-proxies them directly to `backendTarget`, eliminating CORS errors, browser port confusion, and hardcoded URLs.

### 2.3 Process Management & Targeted Shutdown (`logs/runtime/`)
Runtime state and process IDs are saved in `logs/runtime/`:
- `logs/runtime/runtime.json` — Comprehensive runtime registry containing active ports, PIDs, URLs, and allocation timestamps.
- `logs/runtime/backend.pid` — Exact process ID of the FastAPI uvicorn process.
- `logs/runtime/frontend.pid` — Exact process ID of the Vite development server.

`stop.bat` and `port_manager.py stop` read the tracked PIDs, verify that the process image matches (`python.exe`, `node.exe`), and terminate only the specific PIDs via `taskkill /F /T /PID <pid>`. Unrelated Python, Node, or background processes on the user's laptop are never terminated.

---

## 3. Empirical Test Suite Results

The complete test suite was executed via `tools/test_port_allocation.py`. All seven test scenarios passed with 100% success.

```text
===========================================================================
FISHVISION AI — DYNAMIC PORT ALLOCATION & PROCESS ISOLATION TEST SUITE
===========================================================================
```

### Scenario 1: Both Preferred Ports Available (8000 & 5173)
- **Condition:** All candidate ports free.
- **Backend Allocated:** `8000` (`[START]`)
- **Frontend Allocated:** `5173` (`[START]`)
- **Result:** **PASS**

### Scenario 2: Backend Port 8000 Occupied by Unrelated Application
- **Condition:** Third-party TCP socket held open on `127.0.0.1:8000`.
- **Allocator Action:** Port 8000 identified as non-FishVision occupied -> Skipped.
- **Backend Allocated:** `8001` (First fallback port)
- **Frontend Allocated:** `5173` (Preferred port)
- **Third-Party Socket:** Remained listening on 8000 unharmed.
- **Result:** **PASS**

### Scenario 3: Frontend Port 5173 Occupied by Unrelated Application
- **Condition:** Third-party TCP socket held open on `127.0.0.1:5173`.
- **Allocator Action:** Port 5173 identified as occupied -> Skipped.
- **Backend Allocated:** `8000` (Preferred port)
- **Frontend Allocated:** `5174` (First fallback port)
- **Third-Party Socket:** Remained listening on 5173 unharmed.
- **Result:** **PASS**

### Scenario 4: Both Preferred Ports Occupied (8000 & 5173)
- **Condition:** Third-party TCP sockets held open on both 8000 and 5173.
- **Backend Allocated:** `8001` (Fallback port)
- **Frontend Allocated:** `5174` (Fallback port)
- **Result:** **PASS**

### Scenario 5: Multiple Candidate Ports Occupied (8000 & 8001 Occupied)
- **Condition:** Third-party TCP sockets held open on 8000 and 8001.
- **Allocator Action:** Skipped 8000, skipped 8001 -> Allocated next candidate.
- **Backend Allocated:** `8002` (Second fallback port)
- **Frontend Allocated:** `5173` (Preferred port)
- **Third-Party Sockets:** Both 8000 and 8001 remained active and unharmed.
- **Result:** **PASS**

---

### Scenario 6: Five-Model Inference Regression on Fallback Ports (8001 & 5174)
- **Condition:** Backend started on `http://127.0.0.1:8001`, Frontend on `http://127.0.0.1:5174`.
- **Health Readiness Polling:** `tools/check_readiness.py --backend-port 8001 --frontend-port 5174`
  - `GET http://127.0.0.1:8001/health` $\rightarrow$ `200 OK` (`status: ok`, `models: 5`)
  - `GET http://127.0.0.1:5174/` $\rightarrow$ `200 OK`
  - `GET http://127.0.0.1:5174/api/health` (Proxy) $\rightarrow$ `200 OK`
- **Direct Backend Prediction (`POST http://127.0.0.1:8001/predict`):**
  - Status: `200 OK`
  - Consensus: `Gold Fish` (5 of 5 models agreeing — 100% Unanimous)
- **Proxied Frontend Prediction (`POST http://127.0.0.1:5174/api/predict`):**
  - Status: `200 OK`
  - Consensus: `Gold Fish` (5 of 5 models agreeing — 100% Unanimous)

#### Individual Model Inference Evidence on Fallback Ports:
| Model Backbone | Architecture Family | Prediction | Confidence | Latency (CPU) |
| :--- | :--- | :--- | :--- | :--- |
| **DINOv2** | `vit_base_patch14_reg4_dinov2.lvd142m` | `Gold Fish` | **100.0%** | 4282.7 ms |
| **ViT-B/16** | `vit_base_patch16_224` | `Gold Fish` | **80.0%** | 961.8 ms |
| **ConvNeXt Tiny** | `convnext_tiny` | `Gold Fish` | **87.9%** | 377.8 ms |
| **Swin Tiny** | `swin_tiny_patch4_window7_224` | `Gold Fish` | **84.3%** | 648.6 ms |
| **MobileNetV3** | `mobilenetv3_large_100` | `Gold Fish` | **79.3%** | 84.5 ms |

- **Result:** **PASS** (Zero network leakage, full ensemble agreement).

---

### Scenario 7: Safe Shutdown Test (`stop.bat`)
- **Execution:** `python tools/port_manager.py stop`
- **Action:**
  - Located tracked PIDs in `logs/runtime/runtime.json`.
  - Terminated only FishVision services via targeted PID taskkill.
- **Verification:**
  - Unrelated dummy socket on port `8000` verified still listening: `True`.
  - Unrelated dummy socket on port `5173` verified still listening: `True`.
  - Fallback ports `8001` and `5174` cleanly released: `True`.
- **Result:** **PASS**

---

## 4. Test Summary Matrix

| # | Test Scenario | Expected Outcome | Actual Evidence | Status |
| :---: | :--- | :--- | :--- | :---: |
| **1** | Preferred Ports Available | Backend 8000, Frontend 5173 | Backend 8000, Frontend 5173 | **PASS** |
| **2** | Backend 8000 Occupied | Fallback Backend 8001, Frontend 5173 | Backend 8001, Frontend 5173 | **PASS** |
| **3** | Frontend 5173 Occupied | Backend 8000, Fallback Frontend 5174 | Backend 8000, Fallback Frontend 5174 | **PASS** |
| **4** | Both Preferred Occupied | Fallback 8001 & Fallback 5174 | Backend 8001, Frontend 5174 | **PASS** |
| **5** | Multi-Port Fallback | Fallback 8002 when 8000/8001 held | Backend 8002 allocated; sockets intact | **PASS** |
| **6** | 5-Model Live Prediction | Direct & proxied HTTP 200, 5/5 consensus | Gold Fish unanimous (5/5) via 8001 & 5174 | **PASS** |
| **7** | Safe Targeted Shutdown | Only FishVision PIDs killed | Sockets on 8000 & 5173 alive; ports freed | **PASS** |

---

## 5. Certification

The dynamic port allocation system adheres strictly to project preservation rules:
- No model weights, architectures, preprocessing, or class mappings were modified.
- Dynamic project root detection (`%~dp0` normalization) is preserved across all batch scripts.
- Port allocation operates automatically and safely without administrative privileges.

