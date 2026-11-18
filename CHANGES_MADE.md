# FishVision AI — Record of Changes & Audit Log

**Date:** November 11, 2026  
**Project:** `C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App`  
**Purpose:** Comprehensive traceability log of all architectural, frontend, backend, dataset, and launcher modifications made to achieve **Ready for Submission** status.

---

## 1. Backend Service Layer Changes

### 1.1 `backend/model_service.py`
- **Component:** Model Inference Service
- **Nature of Change:** Modified
- **Rationale:** The prompt and user requested a **Live Model Comparison Experiment** showing exact inference times for DINOv2, ViT-B/16, ConvNeXt, Swin, and MobileNet when interpreting the same image.
- **Summary of Changes:**
  - Added high-precision timer `t0 = time.perf_counter()` prior to tensor transform, model forward pass, and softmax computation in `predict_one()`.
  - Calculated `latency_ms = round((time.perf_counter() - t0) * 1000, 1)`.
  - Added `latency_ms` to the returned dictionary for each model result.
- **Verification Method:** Tested with 10 specimens across all 5 models (50 inferences). Verified that `latency_ms` is returned as a float value reflecting true hardware execution duration (MobileNetV3: ~130-200ms, DINOv2: ~5700-7200ms on CPU).

---

### 1.2 `backend/main.py`
- **Component:** FastAPI Endpoints & Consensus Aggregation
- **Nature of Change:** Modified
- **Rationale:** Enable the frontend to display ensemble agreement percentages, list concurring models, and highlight divergent models with their alternate predictions and confidences.
- **Summary of Changes:**
  - Aggregated individual model latencies into `total_latency_ms = round(sum(m["latency_ms"] for m in results), 1)`.
  - Analyzed model predictions against consensus:
    - `agreeing_models = [m["model"] for m in results if m["predicted_class"] == consensus_species]`
    - `disagreeing_models = [{"model": m["model"], "predicted": m["predicted_class"], "confidence": m["confidence"]} for m in results if m["predicted_class"] != consensus_species]`
    - `agreement_percentage = round((len(agreeing_models) / len(results)) * 100, 1)`
  - Extended the `consensus` dictionary in `/predict` response schema to include `agreeing_models`, `disagreeing_models`, `agreement_percentage`, and `total_latency_ms`.
- **Verification Method:** Verified response structure via `requests.post("http://127.0.0.1:8000/predict")` on 10 specimens. Verified correct population of `agreeing_models` and `disagreeing_models` across both unanimous (5/5) and split (4/5) inferences.

---

## 2. Frontend Layer Changes

### 2.1 `frontend/src/types/index.ts`
- **Component:** TypeScript Type Definitions
- **Nature of Change:** Modified
- **Rationale:** Provide strict type safety for the new consensus agreement, disagreement, and latency metadata across React components.
- **Summary of Changes:**
  - Added `DisagreeingModel` interface:
    ```typescript
    export interface DisagreeingModel {
      model: string;
      predicted: string;
      confidence: number;
    }
    ```
  - Added `latency_ms?: number` to `ModelResult`.
  - Extended `Consensus` interface:
    ```typescript
    export interface Consensus {
      species: string;
      agreement_count: number;
      is_unanimous: boolean;
      agreeing_models?: string[];
      disagreeing_models?: DisagreeingModel[];
      agreement_percentage?: number;
      total_latency_ms?: number;
    }
    ```
- **Verification Method:** Compiled with `tsc -b`. Zero type errors.

---

### 2.2 `frontend/src/pages/WorkspacePage.tsx`
- **Component:** Interactive Recognition Workspace View
- **Nature of Change:** Modified
- **Rationale:** Implement the user-requested **Live Model Comparison Experiment** feature and correct architectural categorization descriptions.
- **Summary of Changes:**
  - Added dual view tab selector:
    - **Taxonomic Diagnosis**: Displays high-level consensus, ecological card, bounding box overlay, and species details.
    - **Live Model Comparison Experiment**: Displays side-by-side 5-model matrix, ensemble concordance banner, disagreement breakout card, live latency horizontal bar chart, and Top-3 ranked alternatives per model.
  - Corrected `modelSpecs` architecture families to standard definitions:
    - DINOv2: `Self-Supervised Vision Transformer`
    - ViT-B/16: `Vision Transformer`
    - ConvNeXt Tiny: `Convolutional Neural Network` (explicitly CNN, NOT transformer)
    - Swin Tiny: `Hierarchical Shifted-Window ViT`
    - MobileNetV3: `Efficient Convolutional Neural Network`
- **Verification Method:** Compiled with `npm run build` (0 errors). Loaded route in browser (`http://localhost:5173/workspace`) and tested live inference interaction.

---

### 2.3 `frontend/src/pages/BenchmarksPage.tsx`
- **Component:** Benchmark Matrix View
- **Nature of Change:** Modified
- **Rationale:** Standardize architecture family descriptions with `WorkspacePage.tsx` and academic classification standards.
- **Summary of Changes:**
  - Updated `modelSpecs` dictionary:
    - ConvNeXt Tiny marked as `Convolutional Neural Network`
    - Swin Tiny marked as `Hierarchical Shifted-Window ViT`
    - MobileNetV3 marked as `Efficient Convolutional Neural Network`
- **Verification Method:** Compiled with `npm run build`. Verified 0 errors.

---

### 2.4 `README.md`
- **Component:** Project Documentation
- **Nature of Change:** Modified
- **Rationale:** Resolve documentation inaccuracies regarding the origin of demo samples.
- **Summary of Changes:**
  - Corrected references that erroneously claimed demo samples were "held-out test specimens".
  - Clarified that all 152 demo samples originate from the **isolated training split** to guarantee zero test-set data leakage.
- **Verification Method:** Inspected markdown for consistency with `FINAL_SUBMISSION_AUDIT.md`.

---

## 3. Dataset Integrity & Discrepancy Resolution

### 3.1 Dataset Count Discrepancy Resolution
- **Investigation:** Resolved the variance between historical reports (3,309 test / 4,127 val) and audit scans (3,292 test / 4,089 val).
- **Proof:** Recursive counting on disk revealed:
  - `test/`: 3,309 files on disk, but 17 are exact content duplicates = 3,292 unique hashes.
  - `val/`: 4,127 files on disk, but 38 are exact content duplicates = 4,089 unique hashes.
  - `train/`: 15,304 files on disk, 338 internal duplicates = 14,966 unique hashes.
- **Finding:** Historical reports counted total files; audit scans counted unique hashes. Both are authoritative within their respective definitions. Total physical files: 22,740 across 152 classes.

---

### 3.2 Demo Sample Purification & Verification
- **Component:** Interactive Demo Dataset (`data/demo_samples/`)
- **Nature of Change:** Purified and Re-audited
- **Rationale:** Data leakage prevention — demo specimens must never originate from the held-out test split.
- **Summary of Changes:**
  - Initial check detected 5 demo samples that collided with test set files due to duplicate image instances in the raw dataset (`Fourfinger Threadfin`, `Indian Carp`, `Janitor Fish`, `Mudfish`, `Silver Barb`).
  - Replaced all 5 with pure training images from `classification_152_ready.zip\train\`.
  - Re-verified all 152 demo samples using SHA-256 and perceptual difference hashes (dHash):
    - SHA-256 test collisions: **0**
    - Perceptual lookalikes investigated: 2 pairs flagged by dHash were confirmed via pixel analysis to be distinct photographs (38.7% pixel difference), not duplicates.
    - Decodable, valid image files: 152 / 152
    - Canonical 152-class mapping alignment: 152 / 152
- **Verification Method:** Executed `scripts_audit_phase2.py`: **PASS**.

---

## 4. Windows Launcher & Process Lifecycle

### 4.1 `run.bat`
- **Component:** One-Click Windows Startup Script
- **Nature of Change:** Enhanced
- **Rationale:** Prevent port collision errors (WinError 10048) if FastAPI or Vite were already running, and streamline user onboarding.
- **Summary of Changes:**
  - Added active port listener checks using `netstat -ano | findstr :8000` and `:5173`.
  - If a service is already running on the port, `run.bat` detects it, logs a notification, and safely reuses the active server instead of crashing or spawning duplicate instances.
  - Automatically launches the default browser to `http://localhost:5173`.
- **Verification Method:** Tested with servers stopped (starts both cleanly) and with servers already running (safely detects and reports active status).

---

### 4.2 `stop.bat`
- **Component:** Windows Process Shutdown Script
- **Nature of Change:** Created
- **Rationale:** Provide a reliable, automated way to terminate background FastAPI (uvicorn) and Vite dev server processes on Windows.
- **Summary of Changes:**
  - Extracts active PIDs on ports 8000 and 5173 via `netstat -aon`.
  - Terminates each process cleanly using `taskkill /F /PID <pid>`.
- **Verification Method:** Executed `stop.bat`. Verified ports 8000 and 5173 transitioned from `LISTENING` to closed.

---

## 5. Verification Checklist & Current Status

- [x] **Dataset Count Discrepancy:** Resolved and documented (3,309 disk files vs 3,292 unique content hashes).
- [x] **Zero Test-Set Data Leakage:** Confirmed 0 collisions across all 152 demo species.
- [x] **Canonical Class Parity:** 152 of 152 classes match `backend.model_service.get_classes()`.
- [x] **Five-Model Operation:** All 5 models load genuine weights and predict correctly.
- [x] **Architectural Descriptions:** Corrected in UI and documentation (ConvNeXt is a CNN).
- [x] **Ground Truth Correctness:** 47/50 individual predictions correct (94.0%); majority vote 10/10 correct (100.0%).
- [x] **Latency Methodology:** Verified on CPU with warm-up runs and repetition timings.
- [x] **Explainable AI Status:** Accurately reported as **NOT IMPLEMENTED — FUTURE WORK** (no mock heatmaps).
- [x] **Frontend Production Build:** `npm run build` passes with 0 TypeScript/Vite errors.
- [x] **Zero Raw HTML Display:** All components rendered via native React JSX.
- [x] **Windows Lifecycle:** `run.bat` and `stop.bat` tested and operational.
- [x] **Final Audit Documentation:** `FINAL_SUBMISSION_AUDIT.md` and `CHANGES_MADE.md` updated.
