from pathlib import Path
import gc, json, threading
import torch
import timm
from PIL import Image
from torchvision import transforms
from huggingface_hub import hf_hub_download
from .config import CONFIG, HF_TOKEN, HF_REPO_ID, DEVICE, ROOT

torch.set_num_threads(max(1, min(4, __import__("os").cpu_count() or 2)))
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)
_lock = threading.Lock()
_classes = None
_model_cache = {}  # Caches loaded models in RAM for instant inference

def get_classes():
    global _classes
    if _classes is not None:
        return _classes
    candidates = CONFIG.get("class_mapping_candidates", [])
    for remote in candidates:
        try:
            local_candidate = ROOT / remote
            if local_candidate.exists():
                data = json.loads(local_candidate.read_text(encoding="utf-8"))
            else:
                path = hf_hub_download(repo_id=HF_REPO_ID, filename=remote,
                                       repo_type="model", token=HF_TOKEN or None)
                data = json.loads(Path(path).read_text(encoding="utf-8"))
            if "idx_to_class" in data:
                names = data["idx_to_class"]
                if isinstance(names, dict):
                    names = [names[str(i)] for i in range(152)]
                _classes = list(names)
                break
            if "class_to_idx" in data:
                mapping = data["class_to_idx"]
                _classes = [k for k, v in sorted(mapping.items(), key=lambda x: x[1])]
                break
        except Exception:
            pass
    if _classes is None:
        cfg = next(x for x in CONFIG["models"] if x["key"] == "ViT-B/16")
        local_ckpt = ROOT / cfg["filename"]
        if local_ckpt.exists():
            ckpt_path = str(local_ckpt)
        else:
            ckpt_path = hf_hub_download(repo_id=HF_REPO_ID, filename=cfg["filename"],
                                        repo_type="model", token=HF_TOKEN or None)
        raw = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        if isinstance(raw, dict) and isinstance(raw.get("class_to_idx"), dict):
            _classes = [k for k, v in sorted(raw["class_to_idx"].items(), key=lambda x: x[1])]
    if not _classes or len(_classes) != 152:
        raise RuntimeError(
            "Could not recover the 152-class canonical mapping. "
            "Ensure final_deployment_package/class_mapping.json exists in the HF repo."
        )
    return _classes

def _get_tta_batches(image: Image.Image, spec: dict):
    """Generates both Full-Square Resize and Aspect-Preserving CenterCrop views."""
    size = spec["image_size"]
    tf_square = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)
    ])
    if spec["key"] == "DINOv2":
        return tf_square(image).unsqueeze(0)
    
    # For 224x224 models: combine full-fish square view + center-crop view
    tf_crop = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)
    ])
    return torch.stack([tf_square(image), tf_crop(image)], dim=0)

def _state_dict(raw):
    if isinstance(raw, dict):
        for key in ("model_state_dict", "state_dict", "model", "model_state", "net"):
            if key in raw and isinstance(raw[key], dict):
                raw = raw[key]
                break
    if not isinstance(raw, dict):
        raise RuntimeError("Unsupported checkpoint format.")
    cleaned = {}
    for key, value in raw.items():
        while key.startswith("module."):
            key = key[len("module."):]
        if torch.is_tensor(value):
            cleaned[key] = value
    if not cleaned:
        raise RuntimeError("No tensor weights found in checkpoint.")
    return cleaned

def _load_model(spec):
    key = spec["key"]
    if key in _model_cache:
        return _model_cache[key]
        
    local_path = ROOT / spec["filename"]
    if local_path.exists():
        path = str(local_path)
    else:
        path = hf_hub_download(repo_id=HF_REPO_ID, filename=spec["filename"],
                               repo_type="model", token=HF_TOKEN or None)
    kwargs = {"pretrained": False, "num_classes": CONFIG["num_classes"]}
    if key == "DINOv2":
        kwargs["img_size"] = 518
    model = timm.create_model(spec["architecture"], **kwargs)
    raw = torch.load(path, map_location="cpu", weights_only=False)
    state = _state_dict(raw)
    model.load_state_dict(state, strict=True)
    model.eval()
    _model_cache[key] = model
    return model

def predict_one(image: Image.Image, spec: dict, top_k=5):
    import time
    t0 = time.perf_counter()
    classes = get_classes()
    with _lock:
        model = _load_model(spec)
        x = _get_tta_batches(image.convert("RGB"), spec)
        with torch.inference_mode():
            logits = model(x)
            probs = torch.softmax(logits, dim=1).mean(dim=0)
        k = min(top_k, len(classes))
        values, indices = torch.topk(probs, k=k)
        top = [{"species": classes[int(i)], "confidence": round(float(v)*100, 4)}
               for v, i in zip(values, indices)]
        t1 = time.perf_counter()
        return {"model": spec["name"], "prediction": top[0]["species"],
                "confidence": top[0]["confidence"], "top5": top,
                "latency_ms": round((t1 - t0) * 1000, 1)}