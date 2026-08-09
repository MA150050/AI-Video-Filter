# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from pathlib import Path
import os, shutil
from huggingface_hub import snapshot_download
import yaml

ROOT=Path(__file__).resolve().parents[1]
CFG=yaml.safe_load((ROOT/"config/config.yaml").read_text(encoding="utf-8"))

def hf(model_id,dst):
    dst.mkdir(parents=True,exist_ok=True); marker=dst/".installed"
    if marker.exists(): print("[OK]",model_id); return
    snapshot_download(repo_id=model_id,local_dir=str(dst),local_dir_use_symlinks=False,resume_download=True)
    marker.write_text(model_id,encoding="utf-8")

def main():
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY","1")
    hf(CFG["models"]["nsfw"]["id"],ROOT/CFG["models"]["nsfw"]["local_dir"])
    hf(CFG["models"]["xclip"]["id"],ROOT/CFG["models"]["xclip"]["local_dir"])
    # Ultralytics downloads the person detector once; then it is fully local.
    from ultralytics import YOLO
    d=ROOT/CFG["models"]["person"]["local_dir"]; d.mkdir(parents=True,exist_ok=True)
    pt=d/CFG["models"]["person"]["filename"]
    if not pt.exists():
        model=YOLO(CFG["models"]["person"]["filename"])
        src=Path(model.ckpt_path)
        shutil.copy2(src,pt)
    print("[OK] person model:",pt)

if __name__=="__main__": main()
