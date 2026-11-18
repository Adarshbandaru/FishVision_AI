# FishVision AI — Intelligent Marine Species Recognition Platform (v2.4)

FishVision AI is an academic research platform and multi-model neural ensemble framework benchmarked across **152 distinct fish taxa** (22,741 annotated specimens) with zero-shot and fine-grained taxonomic recognition capabilities.

The platform pairs a high-performance **FastAPI (Python) ML inference backend** with a **React 19 + TypeScript + Vite + Tailwind CSS** frontend inspired by Google Stitch oceanic design aesthetics.

---

## One-Click Windows Quick Start

FishVision AI is engineered for **zero-configuration portability** across Windows 10/11 laptops. Teammates do not need to manually configure Python virtual environments, pip packages, or npm dependencies.

### Option A: Complete Automatic Launch (Recommended)
1. Extract the project folder anywhere on your computer.
2. **Double-click `run.bat`**.

That's it! The launcher automatically:
- Checks for Python 3.12 and Node.js LTS (auto-installs via `winget` if missing).
- Configures an isolated `.venv` and installs all locked backend dependencies.
- Installs all React + Vite dependencies via `npm ci`.
- Audits all 5 local `.pth` model checkpoints (~930 MB) and canonical 152-class mappings.
- Launches the FastAPI backend on `http://127.0.0.1:8000`.
- Launches the React + Vite frontend on `http://127.0.0.1:5173`.
- Polls service health and automatically opens `http://localhost:5173` in your default browser.

### Option B: Dedicated First-Time Setup
If you prefer to perform environment preparation and production build verification upfront before launching:
1. **Double-click `FIRST_TIME_SETUP.bat`**.
2. Once the 8-phase setup reports `SUCCESS`, **double-click `run.bat`** to start the application.

### Stopping the Application
When finished evaluating the platform:
- **Double-click `stop.bat`**.
- This safely terminates only the specific processes listening on ports 8000 and 5173, releasing ports immediately without affecting any other running programs.

---

## Architecture Overview

```
FishVision_V2_App/
├── FIRST_TIME_SETUP.bat            # 8-phase automated setup and validation script
├── run.bat                         # One-click Windows startup script with health polling
├── stop.bat                        # Clean background process shutdown script
├── requirements.txt                # Locked Python backend dependencies
├── checkpoints/                    # 5 Local Fine-Tuned Model Weights (~930 MB)
│   ├── DINOv2_MasterBest_152.pth   # 330.8 MB (Top-1: 93.90%)
│   ├── ViT_B16_V2_Best_152.pth     # 327.8 MB (Top-1: 88.33%)
│   ├── ConvNeXt_Tiny_Best_152.pth  # 106.6 MB (Top-1: 87.40%)
│   ├── Swin_Tiny_Best_152.pth      # 105.5 MB (Top-1: 85.13%)
│   └── MobileNetV3_Best_152.pth    # 17.0 MB  (Top-1: 70.32%)
├── backend/                        # FastAPI ML & CV Backend
│   ├── main.py                     # API routing, CORS, and inference endpoints
│   ├── model_service.py            # PyTorch + timm 5-model inference & TTA
│   ├── cv_service.py               # CPU-safe detection, segmentation & crop extraction
│   └── config.py                   # Environment, model config, and device settings
├── data/
│   ├── class_mapping.json          # Canonical 152 fish taxa index
│   ├── demo_samples/               # 152 genuine isolated training specimens (.jpg)
│   │   └── sample_manifest.json    # Complete metadata catalog for all 152 samples
│   ├── species_metadata.json       # Ecological biology, diet, size, and status
│   └── verified_metrics.json       # Frozen test set benchmark metrics
├── frontend/                       # Modern React + Vite Single Page Application
│   ├── src/
│   │   ├── components/             # Reusable UI & interactive modals (Gallery, Quiz)
│   │   ├── layouts/                # AppLayout with persistent Stitch sidebar
│   │   ├── pages/                  # 6 Core Screens
│   │   │   ├── DashboardPage.tsx   # System overview & telemetry KPIs
│   │   │   ├── WorkspacePage.tsx   # Recognition workspace & 5-model comparison
│   │   │   ├── CatalogPage.tsx     # 152 species searchable taxonomic catalog
│   │   │   ├── BenchmarksPage.tsx  # Recharts matrix & frozen test metrics
│   │   │   ├── HistoryPage.tsx     # Persistent evaluation audit log & JSON export
│   │   │   └── MethodologyPage.tsx # Technical specifications & research citations
│   │   ├── services/api.ts         # Centralized Axios API client
│   │   ├── types/index.ts          # TypeScript domain interfaces
│   │   └── utils/historyStore.ts   # LocalStorage persistence for predictions
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── tools/
│   ├── verify_setup.py             # Pre-flight environment & checkpoint audit
│   ├── check_readiness.py          # HTTP health polling waiter
│   └── test_live_inference.py       # Live multi-model prediction test script
├── logs/                           # Automated execution logs
│   ├── setup.log                   # Installation and build traces
│   ├── backend.log                 # FastAPI uvicorn server output
│   └── frontend.log                # Vite development server output
└── PORTABLE_DEPLOYMENT_REPORT.md   # Comprehensive engineering release audit
```

---

## 5 Fine-Tuned Neural Backbones

All models are evaluated on a **strictly held-out test split of 3,309 images**:

| Model | Architecture Family | Input Res | Parameters | Top-1 Accuracy | Macro F1 | Checkpoint Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DINOv2** | Self-Supervised ViT with Registers | 518×518 | 86M | **93.90%** | **86.96%** | `checkpoints/` (Offline Ready) |
| **ViT-B/16** | Supervised Vision Transformer | 224×224 | 86M | **88.33%** | 78.86% | `checkpoints/` (Offline Ready) |
| **ConvNeXt Tiny** | Modernized Pure ConvNet | 224×224 | 28M | **87.40%** | 77.59% | `checkpoints/` (Offline Ready) |
| **Swin Tiny** | Hierarchical Shifted-Window ViT | 224×224 | 28M | **85.13%** | 75.63% | `checkpoints/` (Offline Ready) |
| **MobileNetV3** | Lightweight Edge ConvNet | 224×224 | 5.4M | **70.32%** | 57.36% | `checkpoints/` (Offline Ready) |

> **Offline Architecture Guarantee:** All model weights are bundled directly within the distribution. An internet connection or Hugging Face authentication token is **not required** to run live inferences.

---

## Interactive Features

1. **Surprise Me / Random Specimen Generator**: Instantly loads an authentic specimen from the 152-class training-derived demo catalog into the canvas.
2. **Species-Specific Sampler**: Select any of the 152 taxa from a dropdown to immediately sample genuine imagery of that fish.
3. **Authentic Specimen Gallery Modal**: Visual thumbnail browser across all 152 species with instant "Test in Workspace" action.
4. **Fish Recognition Challenge (Quiz)**: Interactive human-versus-AI recognition game with clues, score and streak tracking, and ground-truth comparison against the 5 models.
5. **Computer Vision ROI Pipeline**: Heuristic and neural detection/segmentation modes with bounding box and contour overlays.
6. **Live Multi-Model Comparison**: Simultaneous inference across all 5 architectures displaying ensemble consensus, individual model predictions, confidence percentages, agreement ratios, and latencies.

---

## Backend API Endpoints

- `GET /health` — System status, device, and loaded model count
- `GET /models` — Specifications for all five fine-tuned architectures
- `GET /classes` — List of all 152 canonical species class names
- `POST /predict` — Multi-part image upload returning 5-model predictions and consensus
- `GET /species` — Comprehensive ecological metadata for all 152 taxa
- `GET /species/{species_name}` — Detailed profile for a single species
- `GET /benchmarks` — Frozen test dataset metrics and partition counts
- `GET /samples/manifest` — Manifest of genuine 152-class demo images (isolated from test split)
- `GET /samples/random?species=` — Randomized specimen selector
- `GET /samples/image/{filename}` — Direct authentic image file streaming
- `GET /cv/status` — Operational status of vision modules
- `POST /cv/detect` — Specimen bounding box ROI detection
- `POST /cv/segment` — Specimen contour segmentation
- `POST /cv/analyze-combined` — ROI crop extraction followed by 5-model classification

---

## Troubleshooting & Diagnostics

### Port Conflicts (Ports 8000 or 5173 Already Bound)
- Run `stop.bat` to terminate any previous instances of FishVision AI.
- If another service (such as WSL or another web application) is using port 8000 or 5173, close that application or terminate WSL port forwarding with `wsl --shutdown` in PowerShell.

### Windows Defender / SmartScreen Popup
- Windows may display a protection prompt when running newly downloaded `.bat` files.
- Click **"More Info"** and then **"Run Anyway"**. All batch files are plain-text scripts that can be inspected in any editor.

### Winget Package Manager Missing
- If `FIRST_TIME_SETUP.bat` reports that `winget` is not available, install:
  1. **Python 3.12** from [python.org](https://www.python.org/downloads/) (ensure **"Add python.exe to PATH"** is checked).
  2. **Node.js LTS** from [nodejs.org](https://nodejs.org/).
- Then re-run `run.bat`.

### Viewing Execution Logs
If a server fails to start, inspect the logs generated in `logs/`:
- `logs/setup.log` — Virtualenv creation, pip install, and npm install output.
- `logs/backend.log` — FastAPI uvicorn stdout and error traces.
- `logs/frontend.log` — React + Vite compilation traces.
