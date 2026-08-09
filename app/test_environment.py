# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from pathlib import Path
import torch, yaml

ROOT=Path(__file__).resolve().parents[1]
CFG=yaml.safe_load((ROOT/"config/config.yaml").read_text(encoding="utf-8"))

def main():
    print("PyTorch:",torch.__version__)
    print("CUDA:",torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:",torch.cuda.get_device_name(0))
        print("CUDA runtime:",torch.version.cuda)
        print("VRAM GB:",round(torch.cuda.get_device_properties(0).total_memory/1024**3,2))
    for p in [
        ROOT/CFG["models"]["nsfw"]["local_dir"]/".installed",
        ROOT/CFG["models"]["xclip"]["local_dir"]/".installed",
        ROOT/CFG["models"]["person"]["local_dir"]/CFG["models"]["person"]["filename"],
    ]:
        print(str(p), "OK" if p.exists() else "MISSING")

if __name__=="__main__": main()
