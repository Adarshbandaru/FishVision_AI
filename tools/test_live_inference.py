import requests
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sample_path = ROOT / "data" / "demo_samples" / "Gold_Fish_sample.jpg"
url = "http://127.0.0.1:8000/predict"

with open(sample_path, "rb") as f:
    resp = requests.post(url, files={"file": ("fish.jpg", f, "image/jpeg")})

print(f"Status Code: {resp.status_code}")
data = resp.json()
c = data.get("consensus", {})
print("Consensus Species:   ", c.get("species"))
print(f"Consensus Agreement: {c.get('agreement_count')}/{c.get('total_models')} ({c.get('agreement_percentage')}%)")
print("Total Latency:       ", data.get("total_latency_ms"), "ms")
print("Model Inferences:")
for r in data.get("results", []):
    m_name = r.get("model")
    pred = r.get("prediction")
    conf = r.get("confidence", 0) * 100
    lat = r.get("latency_ms", 0)
    print(f"  [{m_name:<14}] -> {pred:<25} ({conf:5.1f}%) in {lat:.1f}ms")
