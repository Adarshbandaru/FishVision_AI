import json
import random
from pathlib import Path
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError

from .config import CONFIG, DEVICE, HF_TOKEN, HF_REPO_ID, ROOT
from .model_service import predict_one, get_classes
from .cv_service import get_cv_status, detect_fish_roi, segment_fish_mask, extract_primary_crop

app = FastAPI(
    title="FishVision V2 API",
    version="2.0.0",
    description="152-class fish species recognition using five fine-tuned models with Stitch-inspired UI."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = ROOT / "data"
SPECIES_META_PATH = DATA_DIR / "species_metadata.json"
VERIFIED_METRICS_PATH = DATA_DIR / "verified_metrics.json"
SAMPLES_DIR = DATA_DIR / "demo_samples"
SAMPLE_MANIFEST_PATH = SAMPLES_DIR / "sample_manifest.json"

_species_cache = None
_metrics_cache = None
_sample_manifest_cache = None

def load_species_metadata():
    global _species_cache
    if _species_cache is None:
        if SPECIES_META_PATH.exists():
            _species_cache = json.loads(SPECIES_META_PATH.read_text(encoding="utf-8"))
        else:
            _species_cache = {}
    return _species_cache

def load_verified_metrics():
    global _metrics_cache
    if _metrics_cache is None:
        if VERIFIED_METRICS_PATH.exists():
            _metrics_cache = json.loads(VERIFIED_METRICS_PATH.read_text(encoding="utf-8"))
        else:
            _metrics_cache = {}
    return _metrics_cache

def load_sample_manifest():
    global _sample_manifest_cache
    if _sample_manifest_cache is None:
        if SAMPLE_MANIFEST_PATH.exists():
            _sample_manifest_cache = json.loads(SAMPLE_MANIFEST_PATH.read_text(encoding="utf-8"))
        else:
            _sample_manifest_cache = []
    return _sample_manifest_cache


# ---------------------------------------------------------------------------
# CORE MODEL & SYSTEM ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": DEVICE,
        "repo_id": HF_REPO_ID,
        "hf_token_configured": bool(HF_TOKEN),
        "models": len(CONFIG["models"]),
        "cv_support": True
    }

@app.get("/models")
def models():
    return {"models": [{k: v for k, v in x.items() if k != "filename"} for x in CONFIG["models"]]}

@app.get("/classes")
def classes():
    try:
        cls_list = get_classes()
        return {"count": len(cls_list), "classes": cls_list}
    except Exception as e:
        raise HTTPException(503, str(e))

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/bmp"):
        raise HTTPException(400, "Upload a JPG, PNG, WEBP or BMP image.")
    data = await file.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "Image must be 15 MB or smaller.")
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "The uploaded file is not a valid image.")
    try:
        results = []
        for spec in CONFIG["models"]:
            results.append(predict_one(image, spec, top_k=5))
            
        # Determine agreement and consensus
        predictions = [r["prediction"] for r in results]
        most_common = max(set(predictions), key=predictions.count)
        agreement_count = predictions.count(most_common)
        agreeing_models = [r["model"] for r in results if r["prediction"] == most_common]
        disagreeing_models = [
            {"model": r["model"], "predicted": r["prediction"], "confidence": r["confidence"]}
            for r in results if r["prediction"] != most_common
        ]
        total_latency = sum(r.get("latency_ms", 0.0) for r in results)
        
        return {
            "results": results,
            "best_model": "DINOv2",
            "consensus": {
                "species": most_common,
                "agreement_count": agreement_count,
                "total_models": len(results),
                "is_unanimous": agreement_count == len(results),
                "has_disagreement": agreement_count < len(results),
                "agreeing_models": agreeing_models,
                "disagreeing_models": disagreeing_models,
                "agreement_percentage": round((agreement_count / len(results)) * 100, 1)
            },
            "total_latency_ms": round(total_latency, 1),
            "note": "Live predictions are from the uploaded image. Frozen test metrics are separate."
        }
    except Exception as e:
        raise HTTPException(500, f"Inference failed: {type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# SPECIES METADATA & BENCHMARKS ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/species")
def get_all_species():
    """Returns metadata for all 152 fish species."""
    meta = load_species_metadata()
    return {"count": len(meta), "species": meta}

@app.get("/species/{species_name}")
def get_single_species(species_name: str):
    """Returns metadata for a specific species by class name."""
    meta = load_species_metadata()
    # Direct lookup or case-insensitive search
    if species_name in meta:
        return meta[species_name]
    for k, v in meta.items():
        if k.lower() == species_name.lower():
            return v
    raise HTTPException(404, f"Species '{species_name}' not found in metadata catalog.")

@app.get("/benchmarks")
def get_benchmarks():
    """Returns verified evaluation metrics across the 5 models."""
    return load_verified_metrics()


# ---------------------------------------------------------------------------
# AUTHENTIC SAMPLE GALLERY & DATASET EXPLORATION ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/samples/manifest")
@app.get("/samples/gallery")
def get_samples_manifest():
    """Returns the full manifest of genuine 152-class sample specimens."""
    samples = load_sample_manifest()
    return {"total": len(samples), "samples": samples}

@app.get("/samples/random")
def get_random_sample(species: Optional[str] = Query(None, description="Optional class_name filter")):
    """Returns a random authentic specimen, optionally filtered by species."""
    samples = load_sample_manifest()
    if not samples:
        raise HTTPException(404, "No sample specimens available.")
    if species:
        matching = [s for s in samples if s["class_name"].lower() == species.lower()]
        if not matching:
            raise HTTPException(404, f"No samples found for species '{species}'.")
        chosen = random.choice(matching)
    else:
        chosen = random.choice(samples)
    return chosen

@app.get("/samples/image/{filename}")
def get_sample_image(filename: str):
    """Serves the authentic sample image file directly."""
    # Prevent directory traversal
    clean_filename = Path(filename).name
    image_path = SAMPLES_DIR / clean_filename
    if not image_path.exists():
        raise HTTPException(404, f"Sample image '{clean_filename}' not found.")
    return FileResponse(image_path, media_type="image/jpeg")


# ---------------------------------------------------------------------------
# COMPUTER VISION MODULES (YOLO / SAM / ROI EXTRACTION)
# ---------------------------------------------------------------------------

@app.get("/cv/status")
def cv_status():
    """Returns status of detection and segmentation modules."""
    return get_cv_status()

@app.post("/cv/detect")
async def cv_detect(file: UploadFile = File(...)):
    """Detects fish specimen bounding boxes in the uploaded image."""
    data = await file.read()
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image format.")
    detections = detect_fish_roi(image)
    return {"detections": detections, "count": len(detections)}

@app.post("/cv/segment")
async def cv_segment(file: UploadFile = File(...)):
    """Computes contour segmentation mask for the specimen."""
    data = await file.read()
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image format.")
    result = segment_fish_mask(image)
    return result

@app.post("/cv/analyze-combined")
async def cv_analyze_combined(file: UploadFile = File(...)):
    """
    Combined Pipeline:
    1. Detects fish ROI
    2. Crops to bounding box
    3. Runs 5 fine-tuned classification models on cropped region
    """
    data = await file.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "Image must be 15 MB or smaller.")
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "Invalid image format.")
        
    # 1. Detection
    detections = detect_fish_roi(image)
    primary_box = detections[0]["box_2d"]
    crop = extract_primary_crop(image, primary_box)
    
    # 2. Multi-model classification on crop
    results = []
    for spec in CONFIG["models"]:
        results.append(predict_one(crop, spec, top_k=5))
        
    predictions = [r["prediction"] for r in results]
    most_common = max(set(predictions), key=predictions.count)
    agreement_count = predictions.count(most_common)
    
    return {
        "detection": detections[0],
        "results": results,
        "best_model": "DINOv2",
        "consensus": {
            "species": most_common,
            "agreement_count": agreement_count,
            "total_models": len(results),
            "is_unanimous": agreement_count == len(results),
            "has_disagreement": agreement_count < len(results)
        },
        "pipeline": "ROI Extraction -> 5-Model Ensemble Inference"
    }
