import subprocess
import shutil
import os
from pathlib import Path

src = Path(r"C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App")
test_space = Path(r"C:\Users\adars\Downloads\Test Space Dir\FishVision AI")

if test_space.parent.exists():
    shutil.rmtree(test_space.parent, ignore_errors=True)

test_space.mkdir(parents=True, exist_ok=True)

for d in ['backend', 'frontend', 'checkpoints', 'data', '.venv', 'tools', 'models']:
    target = str(test_space / d)
    source = str(src / d)
    cmd = f'mklink /J "{target}" "{source}"'
    os.system(cmd)

for f in ['run.bat', 'stop.bat', 'FIRST_TIME_SETUP.bat', '.env.example', 'requirements.txt']:
    shutil.copy2(src / f, test_space / f)

print("Created test environment at:", test_space)
for item in test_space.iterdir():
    print(" ", item.name)
