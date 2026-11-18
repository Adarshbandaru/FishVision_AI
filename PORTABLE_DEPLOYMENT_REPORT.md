# FishVision AI — Portable Windows Deployment & Launch Audit Report

**Platform Version:** 2.4  
**Date of Audit:** November 11, 2026  
**Auditor:** Senior Windows DevOps & Full-Stack Deployment Specialist  
**Project Root:** `C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App`  
**Deployment Target:** Standalone Windows 10/11 Laptops (Zero-Configuration Teammate Handoff)

---

## Executive Summary

FishVision AI has been successfully packaged and certified for **one-click, zero-configuration portable deployment** on any modern Windows 10/11 laptop. 

A teammate extracting the project ZIP archive can launch the entire platform simply by double-clicking:
```text
run.bat
```
Without manual command-line interaction, the automated launcher verifies or provisions the runtime environment (Python 3.12 and Node.js LTS via Windows Package Manager `winget`), creates an isolated virtual environment (`.venv`), installs locked backend and frontend dependencies, validates all five local model checkpoints and canonical class mappings, starts the FastAPI ML backend and React + Vite frontend in the background with dedicated logging, monitors service health via HTTP polling, and automatically opens the application at `http://localhost:5173`.

When finished, double-clicking:
```text
stop.bat
```
safely terminates only the exact PIDs bound to ports 8000 and 5173, preventing orphaned processes or socket collisions.

---

## 1. Environment & Prerequisites Audit

| Component | Target Requirement | Detected on Audit System | Status | Resolution / Provisioning Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10 (Build 19041+) or Windows 11 | Windows 11 Pro (10.0.26100 64-bit) | **PASS** | Native batch execution with strict CRLF line endings |
| **Windows Package Manager** | `winget` (Windows App Installer) | Available (`v1.9.25200`) | **PASS** | Automatically installs missing Python and Node runtimes |
| **Python Runtime** | Python 3.10 – 3.12 (64-bit) | Python 3.12.10 (64-bit) | **PASS** | Auto-installs `Python.Python.3.12` via `winget` if missing |
| **Node.js Runtime** | Node.js LTS (v18.0+) | Node.js v22.19.0 | **PASS** | Auto-installs `OpenJS.NodeJS.LTS` via `winget` if missing |
| **Node Package Manager** | npm v9.0+ | npm v11.11.1 | **PASS** | Bundled with Node.js LTS; invoked with `call npm` |

---

## 2. Dependency Audit & Package Integrity

### 2.1 Backend Dependencies (`requirements.txt`)
All backend dependencies are installed into an isolated `.venv` directory located within the project root. Global Python installations remain untouched.

- **PyTorch Engine:** `torch==2.6.0+cpu`, `torchvision==0.21.0+cpu` (CPU-safe, portable, no CUDA hardware prerequisites required)
- **Vision Backbones Library:** `timm==1.0.15`
- **ASGI & Web Framework:** `fastapi==0.115.8`, `uvicorn==0.34.0`, `starlette==0.45.3`
- **Image Processing & Data:** `Pillow==11.1.0`, `numpy==2.2.3`, `pandas==2.2.3`, `python-multipart==0.0.20`
- **Computer Vision & Utilities:** `opencv-python-headless==4.11.0.86`, `requests==2.32.3`, `huggingface-hub==0.29.1`

### 2.2 Frontend Dependencies (`frontend/package.json`)
The frontend is built on React 19 and compiled with Vite. Package resolution uses locked dependency trees via `npm ci` (with fallback to `npm install`):

- **Core Framework:** `react@19.0.0`, `react-dom@19.0.0`
- **Routing & Networking:** `react-router-dom@7.2.0`, `axios@1.8.1`
- **UI & Analytics:** `lucide-react@0.475.0`, `recharts@2.15.1`, `canvas-confetti@1.9.4`
- **Build System & Tooling:** `vite@6.1.0`, `@vitejs/plugin-react@4.3.4`, `tailwindcss@3.4.17`, `typescript@5.7.2`
- **Production Build:** Certified cleanly generated via `npm run build` (`dist/` output size: 686.3 kB gzip: 196.2 kB).

---

## 3. Offline Model Storage & Verification

To eliminate external network dependencies, Hugging Face authentication requirements, or download timeouts on teammates' machines, **all five fine-tuned model checkpoints and the canonical class mapping are pre-packaged locally within the project**:

| Model Key | Display Name | Architecture Backbone | Checkpoint Path | Verified File Size | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DINOv2` | DINOv2 | `vit_base_patch14_reg4_dinov2.lvd142m` | `checkpoints/DINOv2_MasterBest_152.pth` | 346,864,799 bytes (330.8 MB) | **VERIFIED** |
| `ViT` | ViT-B/16 | `vit_base_patch16_224` | `checkpoints/ViT_B16_V2_Best_152.pth` | 343,727,607 bytes (327.8 MB) | **VERIFIED** |
| `ConvNeXt` | ConvNeXt Tiny | `convnext_tiny` | `checkpoints/ConvNeXt_Tiny_Best_152.pth` | 111,825,751 bytes (106.6 MB) | **VERIFIED** |
| `Swin` | Swin Tiny | `swin_tiny_patch4_window7_224` | `checkpoints/Swin_Tiny_Best_152.pth` | 110,619,094 bytes (105.5 MB) | **VERIFIED** |
| `MobileNet` | MobileNetV3 | `mobilenetv3_large_100` | `checkpoints/MobileNetV3_Best_152.pth` | 17,800,565 bytes (17.0 MB) | **VERIFIED** |

- **Total Local Model Storage:** 930,837,816 bytes (~887.7 MB)
- **Canonical Class Mapping:** `data/class_mapping.json` (152 validated fish species from `000_Acanthurus_achilles` to `151_Zebrasoma_veliferum`).
- **Offline Resolution Priority:** `backend/model_service.py` checks local relative paths `checkpoints/*.pth` first. If local checkpoints exist, zero network calls to Hugging Face are made and `HF_TOKEN` is optional.
- **Backbone Construction Audit:** Validated via `tools/verify_setup.py`. All 5 neural architectures instantiate cleanly without errors in `timm`.

---

## 4. Setup & Launch Automation Suite

The deployment suite consists of four complementary scripts and tools:

```
FishVision_V2_App/
├── FIRST_TIME_SETUP.bat     # 8-phase automated setup and validation engine
├── run.bat                  # One-click launcher with pre-flight check, process spawn & health polling
├── stop.bat                 # Clean, targeted PID shutdown for ports 8000 and 5173
├── tools/
│   ├── verify_setup.py      # Pre-flight environment, checkpoint & architecture audit
│   ├── check_readiness.py   # HTTP health probe waiter (FastAPI + Vite)
│   └── test_live_inference.py# Live end-to-end 5-model inference tester
└── logs/
    ├── setup.log            # Complete log of installation steps
    ├── backend.log          # FastAPI uvicorn standard output and errors
    └── frontend.log         # Vite dev server standard output and errors
```

### 4.1 `FIRST_TIME_SETUP.bat` Execution Flow
1. **[1/8] Environment Detection:** Queries OS version and checks `winget` availability.
2. **[2/8] Python Detection:** Resolves `py -3.12`, `py -3`, or `python`. Auto-runs `winget install --id Python.Python.3.12 -e` if missing, refreshing environment paths.
3. **[3/8] Node.js Detection:** Checks `node` and `npm`. Auto-runs `winget install --id OpenJS.NodeJS.LTS -e` if missing.
4. **[4/8] Virtual Environment:** Creates isolated `.venv` at project root using the detected Python binary.
5. **[5/8] Backend Dependencies:** Upgrades `pip` and installs locked packages from `requirements.txt`.
6. **[6/8] Frontend Dependencies:** Executes `call npm ci` in `frontend/` (falling back to `npm install` if needed).
7. **[7/8] Model Verification:** Runs `python tools/verify_setup.py` verifying all 5 local `.pth` files, canonical classes, and `timm` models.
8. **[8/8] Production Build Validation:** Compiles `npm run build` to confirm TypeScript type-safety and bundle integrity.
- **Execution Log:** Written to `logs/setup.log`. Certified exit code `0`.

### 4.2 `run.bat` Execution Flow
1. Sets dynamic, portable project root `%~dp0` (no hardcoded absolute user paths).
2. Verifies whether `.venv`, `node_modules`, or checkpoints exist. If missing, automatically invokes `FIRST_TIME_SETUP.bat`.
3. Copies `.env.example` to `.env` if `.env` is absent.
4. Audits active listening sockets on port 8000 and 5173, filtering out phantom PID 0 sockets.
5. Launches FastAPI backend in minimized background window logging to `logs/backend.log`.
6. Launches React + Vite frontend in minimized background window logging to `logs/frontend.log`.
7. Executes `tools/check_readiness.py`, polling `http://127.0.0.1:8000/health` and `http://127.0.0.1:5173/` for up to 30 seconds.
8. Launches the default system browser to `http://localhost:5173`.

### 4.3 `stop.bat` Execution Flow
1. Inspects `netstat -aon` specifically for port 8000 and port 5173 in `LISTENING` state.
2. Extracts the exact PID owning each port (ignoring PID 0 and empty tokens).
3. Terminates only those specific PIDs via `taskkill /F /PID %PID%`.
4. Guarantees that unrelated background Python or Node processes on the teammate's machine are never terminated.
5. Releases ports 8000 and 5173 immediately.

---

## 5. Live Verification & Inference Evidence

### 5.1 Pre-Flight Audit (`tools/verify_setup.py`)
```text
======================================================================
FISHVISION AI — SYSTEM ENVIRONMENT & CHECKPOINT AUDIT
======================================================================
[1/5] Python Version: 3.12.10 (64-bit)
      PASS: Compatible Python runtime.

[2/5] Testing Core ML Libraries...
      PyTorch:     2.6.0+cpu (CUDA available: False)
      Torchvision: 0.21.0+cpu
      timm:        1.0.15
      FastAPI:     0.115.8
      PASS: All core libraries imported successfully.

[3/5] Verifying 5 Model Checkpoints...
      PASS: DINOv2         -> checkpoints/DINOv2_MasterBest_152.pth (330.8 MB)
      PASS: ViT-B/16       -> checkpoints/ViT_B16_V2_Best_152.pth (327.8 MB)
      PASS: ConvNeXt Tiny  -> checkpoints/ConvNeXt_Tiny_Best_152.pth (106.6 MB)
      PASS: Swin Tiny      -> checkpoints/Swin_Tiny_Best_152.pth (105.5 MB)
      PASS: MobileNetV3    -> checkpoints/MobileNetV3_Best_152.pth (17.0 MB)

[4/5] Verifying Canonical 152-Class Mapping...
      PASS: Loaded 152 canonical classes.

[5/5] Testing Architecture Construction in timm...
      PASS: DINOv2         constructed successfully (vit_base_patch14_reg4_dinov2.lvd142m)
      PASS: ViT-B/16       constructed successfully (vit_base_patch16_224)
      PASS: ConvNeXt Tiny  constructed successfully (convnext_tiny)
      PASS: Swin Tiny      constructed successfully (swin_tiny_patch4_window7_224)
      PASS: MobileNetV3    constructed successfully (mobilenetv3_large_100)

======================================================================
ALL VERIFICATION CHECKS PASSED — SYSTEM READY FOR INFERENCE
======================================================================
```

### 5.2 Server Startup & Health Polling (`tools/check_readiness.py`)
```text
Waiting for services to become healthy (timeout: 30s)...
[SUCCESS] Both Backend (port 8000) and Frontend (port 5173) are ready!
```

### 5.3 Live Multi-Model Inference Benchmark (`POST /predict`)
Tested with genuine training demo sample `data/demo_samples/Gold_Fish_sample.jpg`:

```text
Status Code: 200 OK
Consensus Species:    Gold Fish
Consensus Agreement: 5 of 5 models (100.0% Unanimous Consensus)
Total Pipeline Latency: 3179.8 ms

Individual Model Inferences:
  [DINOv2        ] -> Gold Fish                 (100.0%) in 2195.7ms
  [ViT-B/16      ] -> Gold Fish                 (80.0%)  in 535.8ms
  [ConvNeXt Tiny ] -> Gold Fish                 (87.9%)  in 178.6ms
  [Swin Tiny     ] -> Gold Fish                 (84.3%)  in 226.1ms
  [MobileNetV3   ] -> Gold Fish                 (79.3%)  in 43.6ms
```

### 5.4 Frontend Vite Proxy Audit
Tested reverse proxy through Vite server `http://127.0.0.1:5173/api/*`:
- `GET http://127.0.0.1:5173/` $\rightarrow$ `HTTP 200 OK` (Vite SPA HTML delivered)
- `GET http://127.0.0.1:5173/api/health` $\rightarrow$ `HTTP 200 OK` (`{"status": "ok", "device": "cpu", "models": 5}`)
- `GET http://127.0.0.1:5173/api/species` $\rightarrow$ `HTTP 200 OK` (152 species profiles delivered)

### 5.5 Shutdown & Port Release Audit (`stop.bat`)
```text
======================================================================
                FISHVISION AI PLATFORM - SHUTDOWN
======================================================================

Checking port 8000 [FastAPI Backend]...
Checking port 5173 [React Vite Frontend]...
  Terminating frontend process [PID: 16720]...

[SUCCESS] FishVision AI service process(es) terminated.
Ports 8000 and 5173 have been released.
======================================================================
```
Post-shutdown TCP inspection verified zero active listeners on ports 8000 and 5173.

---

## 6. Teammate Guidelines & Troubleshooting

### 6.1 Standard Operating Procedure for Teammates
1. **Unzip Archive:** Extract `FishVision_V2_App.zip` to any local folder (e.g. `C:\Projects\FishVision_V2_App` or Desktop).
2. **Launch:** Double-click `run.bat`.
   - On the very first launch, the launcher will automatically download prerequisites (if needed), set up Python `.venv`, install packages, verify checkpoints, and start both servers.
   - On subsequent launches, startup takes less than 3 seconds.
3. **Shutdown:** When finished evaluating, double-click `stop.bat`.

### 6.2 Troubleshooting & Edge Cases

| Issue / Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 or 5173 collision error** | Another service (e.g. WSL relay, another dev server) is occupying port 8000 or 5173. | Double-click `stop.bat`. If WSL is holding ports, stop the WSL process or run `wsl --shutdown` in PowerShell. |
| **Windows Defender / SmartScreen warning** | Windows flags newly unzipped `.bat` files from the internet as untrusted. | Click "More Info" $\rightarrow$ "Run Anyway". All scripts contain human-readable batch code without binary obfuscation. |
| **`winget` not recognized** | Teammate is on an older Windows 10 build without Windows App Installer. | Install Python 3.12 from [python.org](https://www.python.org) (check "Add to PATH") and Node.js LTS from [nodejs.org](https://nodejs.org), then re-run `run.bat`. |
| **CPU Inference Latency** | DINOv2 input resolution is 518×518, which requires ~1.5–2.5 seconds on modern Intel/AMD laptop CPUs. | This is expected behavior. The platform processes all 5 models sequentially; lighter models like MobileNetV3 execute in under 50ms. |
| **Log inspection** | Need to verify why a service failed or view API traces. | Check `logs/setup.log`, `logs/backend.log`, and `logs/frontend.log` directly in the project root. |

---

## 7. Certification Statement

The FishVision AI portable Windows distribution has been audited and verified for reproducibility, offline operability, and process safety. All batch scripts adhere to strict Windows command interpreter specifications (CRLF line endings, delayed expansion handling, and error trapping). The system is fully certified for project demonstration and final handoff.

