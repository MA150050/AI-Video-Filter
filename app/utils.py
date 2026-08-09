# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from __future__ import annotations
import json, logging, subprocess
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR, TEMP_DIR, LOG_DIR = ROOT/"output", ROOT/"temp", ROOT/"logs"
for d in (OUTPUT_DIR, TEMP_DIR, LOG_DIR): d.mkdir(parents=True, exist_ok=True)

def load_yaml(path): return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def save_json(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def setup_logging(name):
    logger=logging.getLogger(name); logger.setLevel(logging.INFO); logger.handlers.clear()
    fmt=logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    sh=logging.StreamHandler(); sh.setFormatter(fmt); logger.addHandler(sh)
    fh=logging.FileHandler(LOG_DIR/f"{name}.log", encoding="utf-8"); fh.setFormatter(fmt); logger.addHandler(fh)
    return logger

def find_binary(root, configured_path, executable_name):
    """Find a local bundled binary first, then a system binary."""
    import shutil

    configured = resolve_local(root, configured_path)
    candidates = [
        configured,
        root / "runtime" / "ffmpeg" / "bin" / executable_name,
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    found = shutil.which(executable_name)
    if found:
        return Path(found)

    raise FileNotFoundError(
        f"{executable_name} not found. "
        f"Expected: {configured} or runtime\\ffmpeg\\bin\\{executable_name}, "
        f"or an executable available in Windows PATH."
    )

def ffprobe_json(video, ffprobe):
    r=subprocess.run(
        [str(ffprobe),"-v","error","-show_format","-show_streams","-of","json",str(video)],
        capture_output=True,text=True,check=True
    )
    return json.loads(r.stdout)

def format_ts(sec):
    sec=max(0,float(sec)); h=int(sec//3600); m=int((sec%3600)//60); s=sec%60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def resolve_local(root, value):
    p=Path(value); return p if p.is_absolute() else root/p
