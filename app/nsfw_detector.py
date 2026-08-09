# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact: https://www.facebook.com/profile.php?id=100078064892942
# Version: 0.3.1
# ============================================================

from pathlib import Path
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

class NSFWDetector:
    def __init__(self,cfg,root,logger):
        self.enabled=bool(cfg["models"]["nsfw"]["enabled"])
        self.device="cuda" if torch.cuda.is_available() and cfg["runtime"]["device"]=="cuda" else "cpu"
        self.logger=logger
        if not self.enabled:return
        d=root/cfg["models"]["nsfw"]["local_dir"]
        self.processor=AutoImageProcessor.from_pretrained(str(d),local_files_only=True,use_fast=False)
        self.model=AutoModelForImageClassification.from_pretrained(str(d),local_files_only=True).to(self.device).eval()
        self.labels={int(k):v.lower() for k,v in self.model.config.id2label.items()}
        logger.info("NSFW model: %s",self.device)

    @torch.inference_mode()
    def score_batch(self,frames):
        if not self.enabled or not frames:return []
        x=self.processor(images=[Image.fromarray(f) for f in frames],return_tensors="pt")
        x={k:v.to(self.device) for k,v in x.items()}
        p=torch.softmax(self.model(**x).logits,dim=-1)
        return [{self.labels.get(i,str(i)):float(row[i]) for i in range(row.shape[0])} for row in p]
