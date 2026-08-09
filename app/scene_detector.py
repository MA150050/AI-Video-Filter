# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector

def detect_scenes(video_path, logger):
    video=open_video(str(video_path)); sm=SceneManager()
    sm.add_detector(AdaptiveDetector(adaptive_threshold=3.0,min_scene_len=15,window_width=2))
    sm.detect_scenes(video=video,show_progress=False)
    raw=sm.get_scene_list()
    if not raw:
        return [{"id":1,"start":0.0,"end":float(video.duration.get_seconds())}]
    out=[]
    for i,(s,e) in enumerate(raw,1):
        out.append({"id":i,"start":s.get_seconds(),"end":e.get_seconds()})
    logger.info("Detected %d scenes.",len(out))
    return out
