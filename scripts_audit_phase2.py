import os
import json
import hashlib
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "data" / "demo_samples"
MANIFEST_PATH = DEMO_DIR / "sample_manifest.json"

TRAIN_DIR = Path(os.environ.get("FISHVISION_TRAIN_DIR", str(ROOT.parent / "classification_152_ready.zip" / "train")))
VAL_DIR = Path(os.environ.get("FISHVISION_VAL_DIR", str(ROOT.parent / "classification_152_ready.zip" / "val")))
TEST_DIR = Path(os.environ.get("FISHVISION_TEST_DIR", str(ROOT.parent / "classification_152_ready.zip" / "test")))

def get_hash(p):
    return hashlib.md5(p.read_bytes()).hexdigest()

print("=== PHASE 2: DATASET INTEGRITY & LEAKAGE AUDIT ===")

# 1. Inspect manifest
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
print(f"Total manifest entries: {len(manifest)}")

# 2. Canonical class alignment
from backend.model_service import get_classes
canonical_classes = get_classes()
print(f"Total canonical classes: {len(canonical_classes)}")
print(f"Unique canonical classes: {len(set(canonical_classes))}")

manifest_classes = [item["class_name"] for item in manifest]
print(f"Unique manifest classes: {len(set(manifest_classes))}")

diff = set(canonical_classes).symmetric_difference(set(manifest_classes))
if diff:
    print(f"ERROR: Discrepancies between canonical and manifest: {diff}")
else:
    print("PASS: Exact 1-to-1 match between manifest classes and canonical classes!")

# 3. Image file validation & decodability
corrupted_files = []
unresolvable_paths = []
demo_hashes = {}

for item in manifest:
    fpath = DEMO_DIR / item["filename"]
    if not fpath.exists():
        unresolvable_paths.append(item["filename"])
        continue
    if fpath.stat().st_size == 0:
        corrupted_files.append((item["filename"], "0-byte file"))
        continue
    try:
        with Image.open(fpath) as img:
            img.verify()
        with Image.open(fpath) as img:
            w, h = img.size
            if w <= 0 or h <= 0:
                corrupted_files.append((item["filename"], "invalid dimensions"))
    except Exception as e:
        corrupted_files.append((item["filename"], str(e)))
        continue
        
    h = get_hash(fpath)
    if h in demo_hashes:
        print(f"Duplicate image inside demo_samples: {item['filename']} matches {demo_hashes[h]}")
    demo_hashes[h] = item["filename"]

print(f"Unresolvable image paths: {len(unresolvable_paths)}")
print(f"Corrupted or invalid image files: {len(corrupted_files)}")
print(f"Unique image hashes across 152 demo samples: {len(demo_hashes)}/152")

# 4. Leakage Check against Held-Out Test Set
print("\nScanning Held-Out Test Set for leakage...")
test_hashes = {}
for root, dirs, files in os.walk(TEST_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = Path(root) / f
            test_hashes[get_hash(fp)] = str(fp)

print(f"Total indexed test images: {len(test_hashes)}")

test_leakage = []
for h, name in demo_hashes.items():
    if h in test_hashes:
        test_leakage.append((name, test_hashes[h]))

if test_leakage:
    print(f"CRITICAL LEAKAGE DETECTED: {len(test_leakage)} demo samples overlap with test set!")
    for dname, tpath in test_leakage:
        print(f"  {dname} -> {tpath}")
else:
    print("PASS: ZERO overlap with held-out test set! (0 collisions)")

# 5. Leakage Check against Validation Set
print("\nScanning Validation Set for leakage...")
val_hashes = {}
for root, dirs, files in os.walk(VAL_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = Path(root) / f
            val_hashes[get_hash(fp)] = str(fp)

print(f"Total indexed validation images: {len(val_hashes)}")

val_leakage = []
for h, name in demo_hashes.items():
    if h in val_hashes:
        val_leakage.append((name, val_hashes[h]))

if val_leakage:
    print(f"WARNING: {len(val_leakage)} demo samples overlap with validation set!")
    for dname, vpath in val_leakage:
        print(f"  {dname} -> {vpath}")
else:
    print("PASS: ZERO overlap with validation set! (0 collisions)")

print("\n=== PHASE 2 AUDIT COMPLETE ===")

