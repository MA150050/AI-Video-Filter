# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from __future__ import annotations
from pathlib import Path
import numpy as np
from ultralytics import YOLO

class PersonInteractionTracker:
    def __init__(self,cfg,root,logger):
        self.cfg=cfg; self.logger=logger
        m=cfg["models"]["person"]
        self.enabled=bool(m["enabled"])
        self.device=0 if __import__("torch").cuda.is_available() and cfg["runtime"]["device"]=="cuda" else "cpu"
        self.model=YOLO(str(root/m["local_dir"]/m["filename"]))
        self.names=self.model.names
        logger.info("Person tracker loaded: %s",m["filename"])

    def analyze_frame(self,frame):
        if not self.enabled:return {"people":0,"pairs":[],"intimate_score":0.0,"face_to_face_score":0.0}
        m=self.cfg["models"]["person"]
        result=self.model.track(
            source=frame, persist=True, tracker=m["tracker"],
            conf=m["confidence"], iou=m["iou"], imgsz=m["imgsz"],
            classes=[0], device=self.device, verbose=False
        )[0]
        boxes=result.boxes
        if boxes is None or len(boxes)==0:
            return {"people":0,"pairs":[],"intimate_score":0.0,"face_to_face_score":0.0}

        xyxy=boxes.xyxy.cpu().numpy()
        ids=boxes.id.cpu().numpy().astype(int).tolist() if boxes.id is not None else list(range(len(xyxy)))
        people=[]
        for box,tid in zip(xyxy,ids):
            x1,y1,x2,y2=box
            w=max(1,x2-x1); h=max(1,y2-y1)
            people.append({"id":int(tid),"box":[float(x1),float(y1),float(x2),float(y2)],
                           "cx":float((x1+x2)/2),"cy":float((y1+y2)/2),
                           "w":float(w),"h":float(h)})
        pairs=[]
        intimate_max=0.0; face_max=0.0
        for i in range(len(people)):
            for j in range(i+1,len(people)):
                a,b=people[i],people[j]
                scale=max(1.0,(a["h"]+b["h"])/2)
                dist=((a["cx"]-b["cx"])**2+(a["cy"]-b["cy"])**2)**0.5/scale
                overlap=self._iou(a["box"],b["box"])
                proximity=max(0.0,min(1.0,1.0-dist/1.5))
                # A conservative heuristic: proximity + overlap, not a standalone deletion rule.
                intimate=min(1.0,0.70*proximity+0.30*overlap)
                face=min(1.0,proximity*1.15)
                pairs.append({"a":a["id"],"b":b["id"],"distance_ratio":dist,
                              "overlap":overlap,"proximity_score":proximity,
                              "intimate_score":intimate,"face_to_face_score":face})
                intimate_max=max(intimate_max,intimate); face_max=max(face_max,face)
        return {"people":len(people),"pairs":pairs,
                "intimate_score":float(intimate_max),
                "face_to_face_score":float(face_max)}

    @staticmethod
    def _iou(a,b):
        ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
        ix1=max(ax1,bx1); iy1=max(ay1,by1); ix2=min(ax2,bx2); iy2=min(ay2,by2)
        iw=max(0,ix2-ix1); ih=max(0,iy2-iy1); inter=iw*ih
        aa=max(1,(ax2-ax1)*(ay2-ay1)); ab=max(1,(bx2-bx1)*(by2-by1))
        return inter/max(1,aa+ab-inter)
