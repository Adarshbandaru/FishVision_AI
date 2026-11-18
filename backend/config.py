import json
from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_REPO_ID = os.getenv("HF_REPO_ID", "bandaruadarsh/fishvision-final-experiment").strip()
CONFIG = json.loads((ROOT / "models" / "model_config.json").read_text(encoding="utf-8"))
DEVICE = "cpu"
