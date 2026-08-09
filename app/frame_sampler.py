# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

import cv2, numpy as np

def iter_frames(video_path,start,end,fps):
    cap=cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise RuntimeError(f"Cannot open video: {video_path}")
    try:
        t=float(start); step=1/max(float(fps),0.1)
        while t<end:
            cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
            ok,frame=cap.read()
            if not ok: break
            yield t,cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            t+=step
    finally: cap.release()

def read_clip(video_path,start,end,n_frames):
    cap=cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise RuntimeError(f"Cannot open video: {video_path}")
    try:
        frames=[]; times=np.linspace(start,end,max(2,int(n_frames)))
        for t in times:
            cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
            ok,frame=cap.read()
            if ok: frames.append(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        return frames
    finally: cap.release()
