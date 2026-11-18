import os
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
demo_dir = ROOT / "data" / "demo_samples"
test_dir = Path(os.environ.get("FISHVISION_TEST_DIR", str(ROOT.parent / "classification_152_ready.zip" / "test")))
if not test_dir.exists():
    # Try common local or sibling paths
    for candidate in [ROOT.parent / "test", ROOT / "test", ROOT.parent / "classification_152_ready.zip" / "test"]:
        if candidate.exists():
            test_dir = candidate
            break

def get_hash(p):
    return hashlib.md5(p.read_bytes()).hexdigest()

test_hashes = {}
print("Hashing test images to verify zero test-set overlap...")
for root, dirs, files in os.walk(test_dir):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            fp = Path(root) / f
            test_hashes[get_hash(fp)] = str(fp)

print(f"Total test images hashed: {len(test_hashes)}")

overlap_with_test = []
demo_files = list(demo_dir.glob("*_sample.jpg"))
print(f"Checking {len(demo_files)} demo sample files against test set hashes...")
for df in demo_files:
    h = get_hash(df)
    if h in test_hashes:
        overlap_with_test.append((df.name, test_hashes[h]))

if overlap_with_test:
    print(f"CRITICAL WARNING: Found {len(overlap_with_test)} demo samples that match test set files!")
    for dname, tpath in overlap_with_test[:5]:
        print(f"  {dname} matches {tpath}")
else:
    print("AUDIT SUCCESS: ZERO demo samples originate from the held-out test set! (0 overlap)")

