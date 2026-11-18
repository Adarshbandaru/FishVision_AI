"""
FishVision AI — Environment & Checkpoint Verification Tool
Runs during FIRST_TIME_SETUP.bat and run.bat pre-flight checks.
"""
import sys
import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def verify_all():
    print("=" * 70)
    print("FISHVISION AI — SYSTEM ENVIRONMENT & CHECKPOINT AUDIT")
    print("=" * 70)
    
    # 1. Python version check
    v = sys.version_info
    print(f"[1/5] Python Version: {v.major}.{v.minor}.{v.micro} ({'64-bit' if sys.maxsize > 2**32 else '32-bit'})")
    if v.major != 3 or v.minor < 10 or v.minor > 12:
        print(f"      WARNING: Python 3.10-3.12 is recommended. Current is {v.major}.{v.minor}.")
    else:
        print("      PASS: Compatible Python runtime.")

    # 2. PyTorch & Core Libraries
    print("\n[2/5] Testing Core ML Libraries...")
    try:
        import torch
        import torchvision
        import timm
        import fastapi
        import uvicorn
        from PIL import Image
        import pandas
        print(f"      PyTorch:     {torch.__version__} (CUDA available: {torch.cuda.is_available()})")
        print(f"      Torchvision: {torchvision.__version__}")
        print(f"      timm:        {timm.__version__}")
        print(f"      FastAPI:     {fastapi.__version__}")
        print("      PASS: All core libraries imported successfully.")
    except ImportError as e:
        print(f"      FAIL: Missing required dependency: {e}")
        return False

    # 3. Model Configuration & Checkpoints
    print("\n[3/5] Verifying 5 Model Checkpoints...")
    cfg_path = ROOT / "models" / "model_config.json"
    if not cfg_path.exists():
        print(f"      FAIL: Configuration file missing: {cfg_path}")
        return False
        
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ckpts_dir = ROOT / "checkpoints"
    ckpts_dir.mkdir(exist_ok=True)
    
    missing_models = []
    for spec in cfg["models"]:
        m_name = spec["name"]
        rel_fn = spec["filename"]
        local_file = ROOT / rel_fn
        
        if local_file.exists():
            sz_mb = local_file.stat().st_size / (1024 * 1024)
            print(f"      PASS: {m_name:<14} -> {rel_fn} ({sz_mb:.1f} MB)")
        else:
            print(f"      MISSING: {m_name:<14} -> {rel_fn}")
            missing_models.append(spec)
            
    # Try downloading missing checkpoints if HuggingFace is available
    if missing_models:
        print(f"\n      Attempting to retrieve {len(missing_models)} missing checkpoint(s) via Hugging Face...")
        try:
            from huggingface_hub import hf_hub_download
            from backend.config import HF_REPO_ID, HF_TOKEN
            for spec in list(missing_models):
                print(f"      Downloading {spec['filename']} from {HF_REPO_ID}...")
                p = hf_hub_download(repo_id=HF_REPO_ID, filename=spec["filename"], repo_type="model", token=HF_TOKEN or None)
                target = ROOT / spec["filename"]
                target.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(p, target)
                sz_mb = target.stat().st_size / (1024 * 1024)
                print(f"      Successfully downloaded: {spec['name']} ({sz_mb:.1f} MB)")
                missing_models.remove(spec)
        except Exception as dl_err:
            print(f"      Could not auto-download from Hugging Face: {dl_err}")
            
    if missing_models:
        print("\n      ACTION REQUIRED: Place the missing .pth files in checkpoints/:")
        for m in missing_models:
            print(f"        - {m['filename']}")
        return False

    # 4. Canonical Class Mapping
    print("\n[4/5] Verifying Canonical 152-Class Mapping...")
    try:
        from backend.model_service import get_classes
        classes = get_classes()
        print(f"      PASS: Loaded {len(classes)} canonical classes.")
        if len(classes) != 152:
            print(f"      FAIL: Expected 152 classes, got {len(classes)}.")
            return False
    except Exception as e:
        print(f"      FAIL: Could not load canonical class mapping: {e}")
        return False

    # 5. Model Architecture Instantiation Check
    print("\n[5/5] Testing Architecture Construction in timm...")
    for spec in cfg["models"]:
        m_name = spec["name"]
        arch = spec["architecture"]
        try:
            kwargs = {"pretrained": False, "num_classes": cfg["num_classes"]}
            if spec["key"] == "DINOv2":
                kwargs["img_size"] = 518
            test_m = timm.create_model(arch, **kwargs)
            print(f"      PASS: {m_name:<14} constructed successfully ({arch})")
        except Exception as e:
            print(f"      FAIL: Could not construct {m_name}: {e}")
            return False

    print("\n" + "=" * 70)
    print("ALL VERIFICATION CHECKS PASSED — SYSTEM READY FOR INFERENCE")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)

