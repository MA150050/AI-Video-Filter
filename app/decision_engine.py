# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from collections import defaultdict

def semantic(x):
    def g(*k): return max([float(x.get(i,0)) for i in k] or [0])
    return {
      "kissing":g("two people kissing"),
      "making_out":g("two people making out"),
      "intimate_hug":g("two people hugging intimately"),
      "intimate_scene":g("a sexual or intimate scene"),
      "nude_scene":g("a nude scene"),
      "normal_hug":g("two people embracing"),
      "romantic":g("a romantic but non-intimate scene")
    }

def fuse(events,cfg):
    d=cfg["decision"]; out=[]
    for e in events:
        ns=e.get("nsfw",{})
        best=None
        for k,t in d["nsfw"].items():
            s=float(ns.get(k,0))
            if s>=t and (best is None or s>best[1]): best=(f"NSFW:{k}",s)
        s=semantic(e.get("xclip",{}))
        if best is None:
            checks=[
              ("MAKING_OUT",s["making_out"],d["xclip"]["making_out"]),
              ("KISSING",s["kissing"],d["xclip"]["kissing"]),
              ("INTIMATE_SCENE",s["intimate_scene"],d["xclip"]["intimate_scene"]),
              ("NUDE_SCENE",s["nude_scene"],d["xclip"]["nude_scene"]),
              ("INTIMATE_HUG",s["intimate_hug"],d["xclip"]["intimate_hug"]),
            ]
            for reason,score,thr in checks:
                # Person interaction score must support ambiguous hug/close-contact decisions.
                if reason=="INTIMATE_HUG":
                    support=e.get("interaction",{}).get("intimate_score",0)
                    if score>=thr and support>=cfg["decision"]["interaction"]["intimate_hug"]:
                        best=(reason,score)
                        break
                elif score>=thr:
                    best=(reason,score); break
        if best:
            out.append({**e,"reason":best[0],"score":float(best[1])})
    return out

def temporal_filter(events,cfg):
    groups=defaultdict(list)
    for e in events: groups[e["scene_id"]].append(e)
    out=[]
    win=float(cfg["decision"]["temporal_window_seconds"])
    min_hits=int(cfg["decision"]["temporal_min_hits"])
    for sid,items in groups.items():
        items.sort(key=lambda x:x["time"])
        for e in items:
            hits=[x for x in items if abs(x["time"]-e["time"])<=win]
            # NSFW can be decisive; semantic actions need repeated evidence.
            if e["reason"].startswith("NSFW:") or len(hits)>=min_hits:
                out.append(max(hits,key=lambda x:x["score"]))
    out.sort(key=lambda x:x["time"])
    final=[]
    for e in out:
        if final and e["reason"]==final[-1]["reason"] and abs(e["time"]-final[-1]["time"])<1.0:
            if e["score"]>final[-1]["score"]: final[-1]=e
        else: final.append(e)
    return final

def expand_merge(detections,duration,cfg):
    if not detections:return []
    b=float(cfg["buffer"]["before_seconds"]); a=float(cfg["buffer"]["after_seconds"]); gap=float(cfg["buffer"]["merge_gap_seconds"])
    rs=[{"start":max(0,e["time"]-b),"end":min(duration,e["time"]+a),
         "reason":e["reason"],"score":e["score"]} for e in detections]
    rs.sort(key=lambda x:x["start"]); out=[rs[0]]
    for r in rs[1:]:
        p=out[-1]
        if r["start"]<=p["end"]+gap:
            p["end"]=max(p["end"],r["end"]); p["score"]=max(p["score"],r["score"]); p["reason"]+=f" + {r['reason']}"
        else: out.append(r)
    return out
