# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import torch

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from app.utils import *
from app.scene_detector import detect_scenes
from app.frame_sampler import iter_frames,read_clip
from app.nsfw_detector import NSFWDetector
from app.xclip_detector import XClipDetector
from app.person_tracker import PersonInteractionTracker
from app.decision_engine import fuse,temporal_filter,expand_merge
from app.video_editor import render_clean_video

def state_load(path,video,duration):
    if path.exists():
        try:return json.loads(path.read_text(encoding="utf-8"))
        except Exception:pass
    return {"version":"0.3.0","input":str(video),"duration":duration,"scenes":[],"events":[],"detections":[],"removed":[]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--video",required=True); args=ap.parse_args()
    cfg=load_yaml(ROOT/"config/config.yaml"); logger=setup_logging("ai_video_filter")
    raw_video = args.video.strip()
    if len(raw_video) >= 2 and raw_video[0] == raw_video[-1] and raw_video[0] in ('"', "'"):
        raw_video = raw_video[1:-1]
    video = Path(raw_video).expanduser().resolve()
    if not video.exists():
        raise FileNotFoundError(f"Video file not found: {video}")
    ffprobe=find_binary(ROOT,cfg["runtime"]["ffprobe_path"],"ffprobe.exe")
    info=ffprobe_json(video,ffprobe); duration=float(info["format"].get("duration",0))
    progress=TEMP_DIR/f"{video.stem}.progress.json"; state=state_load(progress,video,duration)
    scenes=state["scenes"] or detect_scenes(video,logger); state["scenes"]=scenes; save_json(progress,state)

    nsfw=NSFWDetector(cfg,ROOT,logger)
    xclip=XClipDetector(cfg,ROOT,logger)
    tracker=PersonInteractionTracker(cfg,ROOT,logger)
    events=state.get("events",[])
    done={e.get("scene_id") for e in events}

    for si,sc in enumerate(scenes,1):
        s,e=float(sc["start"]),float(sc["end"])
        if e-s<cfg["sampling"]["min_scene_seconds"] or sc["id"] in done: continue
        logger.info("[%d/%d] Scene %d %s -> %s",si,len(scenes),sc["id"],format_ts(s),format_ts(e))

        # First pass: NSFW + person interaction at moderate FPS.
        times=[]; frames=[]
        for t,frame in iter_frames(video,s,e,cfg["sampling"]["nsfw_fps"]):
            times.append(t); frames.append(frame)
            if len(frames)>=12:
                scores=nsfw.score_batch(frames)
                for tt,fr,ss in zip(times,frames,scores):
                    inter=tracker.analyze_frame(fr)
                    events.append({"time":tt,"scene_id":sc["id"],"nsfw":ss,"xclip":{},"interaction":inter})
                times=[];frames=[]
        if frames:
            scores=nsfw.score_batch(frames)
            for tt,fr,ss in zip(times,frames,scores):
                inter=tracker.analyze_frame(fr)
                events.append({"time":tt,"scene_id":sc["id"],"nsfw":ss,"xclip":{},"interaction":inter})

        # Second pass: temporal X-CLIP.
        clip=float(cfg["sampling"]["xclip_clip_seconds"]); stride=float(cfg["sampling"]["xclip_stride_seconds"])
        n=int(cfg["sampling"]["xclip_frames"]); t=s
        while t<e:
            ce=min(e,t+clip)
            if ce-t>=1.0:
                fr=read_clip(video,t,ce,n)
                xc=xclip.score_clip(fr) if fr else {}
                if xc:
                    # Attach nearest interaction sample to the temporal center.
                    center=(t+ce)/2
                    nearest=min(
                        (z for z in events if z["scene_id"]==sc["id"]),
                        key=lambda z:abs(z["time"]-center),
                        default={"interaction":{}}
                    )
                    events.append({"time":center,"scene_id":sc["id"],"nsfw":{},"xclip":xc,
                                   "interaction":nearest.get("interaction",{})})
            t+=stride

        state["events"]=events; save_json(progress,state)

    detections=temporal_filter(fuse(events,cfg),cfg)
    ranges=expand_merge(detections,duration,cfg)
    state["detections"]=detections; state["removed"]=ranges; save_json(progress,state)

    output=OUTPUT_DIR/(video.stem+cfg["app"]["output_suffix"]+video.suffix)
    if output.exists() and not cfg["app"]["overwrite_output"]:
        output=OUTPUT_DIR/(video.stem+cfg["app"]["output_suffix"]+"_2"+video.suffix)

    report={"version":"0.3.0","input":str(video),"output":str(output),"duration_seconds":duration,
            "device":"cuda" if torch.cuda.is_available() else "cpu",
            "detections":[{**d,"time_tc":format_ts(d["time"])} for d in detections],
            "removed_ranges":[{**r,"start_tc":format_ts(r["start"]),"end_tc":format_ts(r["end"])} for r in ranges]}
    save_json(LOG_DIR/f"{video.stem}_report.json",report)
    with (LOG_DIR/f"{video.stem}_report.txt").open("w",encoding="utf-8") as f:
        f.write(f"INPUT: {video}\nOUTPUT: {output}\n")
        for r in report["removed_ranges"]:
            f.write(f'{r["start_tc"]} -> {r["end_tc"]} | {r["reason"]} | {r["score"]:.3f}\n')

    render_clean_video(video,output,ranges,cfg,logger)
    logger.info("DONE: %s",output)

if __name__=="__main__":
    try: main()
    except Exception:
        import traceback; traceback.print_exc(); sys.exit(1)
