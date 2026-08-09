from pathlib import Path
import shutil, subprocess, yaml

ROOT = Path(__file__).resolve().parents[1]
cfg = yaml.safe_load((ROOT / "config" / "config.yaml").read_text(encoding="utf-8"))

ff = ROOT / cfg["runtime"]["ffmpeg_path"]
fp = ROOT / cfg["runtime"]["ffprobe_path"]
ff.parent.mkdir(parents=True, exist_ok=True)

for name, target in [("ffmpeg.exe", ff), ("ffprobe.exe", fp)]:
    if target.exists():
        continue

    source = shutil.which(name)
    if source:
        shutil.copy2(source, target)

if not ff.exists() or not fp.exists():
    raise SystemExit(
        "FFmpeg/FFprobe are missing. "
        "Place ffmpeg.exe and ffprobe.exe in runtime\\ffmpeg\\bin\\ "
        "or make them available in Windows PATH, then run INSTALL.bat again."
    )

subprocess.run([str(ff), "-version"], check=True, stdout=subprocess.DEVNULL)
subprocess.run([str(fp), "-version"], check=True, stdout=subprocess.DEVNULL)

print("FFmpeg OK:", ff)
print("FFprobe OK:", fp)
