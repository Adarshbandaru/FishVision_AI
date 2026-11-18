import os
import sys
import json
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "data" / "demo_samples"
MANIFEST_PATH = DEMO_DIR / "sample_manifest.json"

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
base_url = "http://127.0.0.1:8000"

# Pick 10 diverse specimens across the 152 classes
sample_indices = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135]
selected_samples = [manifest[i] for i in sample_indices]

print(f"Selected {len(selected_samples)} representative specimens across 152 taxa:")
for i, s in enumerate(selected_samples):
    print(f"  [{i+1}] {s['common_name']} ({s['class_name']}) -> {s['filename']}")

r_classes = requests.get(f"{base_url}/classes").json()
canonical_classes = set(r_classes["classes"])

inference_audit_results = []

for idx, specimen in enumerate(selected_samples):
    fpath = DEMO_DIR / specimen["filename"]
    t0 = time.perf_counter()
    with open(fpath, "rb") as f:
        r_pred = requests.post(f"{base_url}/predict", files={"file": (specimen["filename"], f, "image/jpeg")})
    total_time = round((time.perf_counter() - t0) * 1000, 1)
    
    if r_pred.status_code != 200:
        print(f"Failed on {specimen['filename']}: {r_pred.status_code}")
        continue
        
    p_data = r_pred.json()
    results = p_data["results"]
    consensus = p_data["consensus"]
    
    print(f"\n[{idx+1}/10] {specimen['common_name']} ({specimen['class_name']}):")
    print(f"      Consensus: '{consensus['species']}' | Agreement: {consensus['agreement_count']}/5")
    if consensus.get("disagreeing_models"):
        print(f"      Disagreements: {consensus['disagreeing_models']}")
    else:
        print(f"      Unanimous Concordance across all 5 models!")
        
    model_details = []
    for m in results:
        m_name = m["model"]
        pred_sp = m["prediction"]
        conf = m["confidence"]
        lat = m.get("latency_ms", "N/A")
        is_canonical = pred_sp in canonical_classes
        print(f"        {m_name:14}: {pred_sp} ({conf:.1f}%) [Latency: {lat} ms]")
        model_details.append({
            "model": m_name,
            "prediction": pred_sp,
            "confidence": conf,
            "latency_ms": lat,
            "top5": m["top5"],
            "in_canonical_classes": is_canonical
        })
        
    inference_audit_results.append({
        "specimen_index": idx + 1,
        "filename": specimen["filename"],
        "ground_truth_class": specimen["class_name"],
        "ground_truth_common": specimen["common_name"],
        "consensus_species": consensus["species"],
        "agreement_count": consensus["agreement_count"],
        "is_unanimous": consensus["is_unanimous"],
        "agreeing_models": consensus.get("agreeing_models", []),
        "disagreeing_models": consensus.get("disagreeing_models", []),
        "total_latency_ms": p_data.get("total_latency_ms", total_time),
        "models": model_details
    })

output_path = ROOT / "audit_inference_evidence_10.json"
output_path.write_text(json.dumps({
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "tested_specimens_count": len(inference_audit_results),
    "results": inference_audit_results
}, indent=2), encoding="utf-8")
print(f"\nSuccessfully audited {len(inference_audit_results)} specimens! Saved to {output_path}")

