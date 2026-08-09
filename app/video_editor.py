# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

import subprocess
from pathlib import Path
from app.utils import find_binary

def render_clean_video(video,output,ranges,cfg,logger):
    root=Path(__file__).resolve().parents[1]
    ff=find_binary(root,cfg["runtime"]["ffmpeg_path"],"ffmpeg.exe")
    probe=find_binary(root,cfg["runtime"]["ffprobe_path"],"ffprobe.exe")
    p=subprocess.run([str(probe),"-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(video)],
                     capture_output=True,text=True,check=True)
    duration=float(p.stdout.strip())
    if not ranges:
        cmd=[str(ff),"-y","-i",str(video),"-map","0:v:0","-map","0:a?",
             "-c:v",cfg["encoding"]["video_codec"],"-preset",cfg["encoding"]["preset"],"-crf",str(cfg["encoding"]["crf"]),
             "-c:a",cfg["encoding"]["audio_codec"],"-b:a",cfg["encoding"]["audio_bitrate"],"-movflags","+faststart",str(output)]
        subprocess.run(cmd,check=True); return
    keep=[]; cur=0.0
    for r in ranges:
        if r["start"]>cur: keep.append((cur,r["start"]))
        cur=max(cur,r["end"])
    if cur<duration: keep.append((cur,duration))
    if not keep: raise RuntimeError("All video content was marked for removal.")
    parts=[]; labels=[]
    for i,(s,e) in enumerate(keep):
        v=f"v{i}"; a=f"a{i}"
        parts += [f"[0:v:0]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[{v}]",
                  f"[0:a:0]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[{a}]"]
        labels.append(f"[{v}][{a}]")
    parts.append("".join(labels)+f"concat=n={len(keep)}:v=1:a=1[outv][outa]")
    cmd=[str(ff),"-y","-i",str(video),"-filter_complex",";".join(parts),
         "-map","[outv]","-map","[outa]","-c:v",cfg["encoding"]["video_codec"],
         "-preset",cfg["encoding"]["preset"],"-crf",str(cfg["encoding"]["crf"]),
         "-c:a",cfg["encoding"]["audio_codec"],"-b:a",cfg["encoding"]["audio_bitrate"],
         "-movflags","+faststart",str(output)]
    logger.info("Rendering %d keep segments.",len(keep)); subprocess.run(cmd,check=True)
