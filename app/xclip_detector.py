# ============================================================
# AI VIDEO FILTER
# Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
# Contact
# Version: 0.3.1 HOTFIX
# ============================================================

from __future__ import annotations

import torch
from transformers import XCLIPProcessor, XCLIPModel


class XClipDetector:
    """Robust local X-CLIP zero-shot video/text scorer.

    X-CLIP expects video pixels shaped:
        [batch, frames, channels, height, width]

    The previous build passed `videos=` directly through the processor,
    which can return no `pixel_values` with some Transformers versions.
    This implementation explicitly processes frames as images and reshapes
    them to the 5-D tensor expected by XCLIPModel.
    """

    def __init__(self, cfg, root, logger):
        self.enabled = bool(cfg["models"]["xclip"]["enabled"])
        self.logger = logger
        self.device = (
            "cuda"
            if torch.cuda.is_available() and cfg["runtime"]["device"] == "cuda"
            else "cpu"
        )

        model_cfg = cfg["models"]["xclip"]
        self.labels = list(model_cfg["labels"])
        self.num_frames = int(model_cfg.get("frames", 8))

        if not self.enabled:
            return

        model_dir = root / model_cfg["local_dir"]

        self.processor = XCLIPProcessor.from_pretrained(
            str(model_dir),
            local_files_only=True,
        )
        self.model = XCLIPModel.from_pretrained(
            str(model_dir),
            local_files_only=True,
        ).to(self.device).eval()

        # Cache text tokens once; text does not change from clip to clip.
        text_inputs = self.processor(
            text=self.labels,
            return_tensors="pt",
            padding=True,
        )
        self.text_inputs = {
            k: v.to(self.device)
            for k, v in text_inputs.items()
            if k in ("input_ids", "attention_mask")
        }

        logger.info(
            "X-CLIP: %s | frames=%d | labels=%d",
            self.device,
            self.num_frames,
            len(self.labels),
        )

    def _normalize_frames(self, frames):
        if not frames:
            return []

        # X-CLIP checkpoint has a fixed temporal position configuration.
        if len(frames) == self.num_frames:
            return frames

        if len(frames) > self.num_frames:
            # Uniform temporal sampling.
            idx = torch.linspace(
                0, len(frames) - 1, self.num_frames
            ).round().long().tolist()
            return [frames[i] for i in idx]

        # Very short scene: repeat the last available frame.
        padded = list(frames)
        while len(padded) < self.num_frames:
            padded.append(padded[-1])
        return padded

    @torch.inference_mode()
    def score_clip(self, frames):
        if not self.enabled or not frames:
            return {}

        frames = self._normalize_frames(frames)

        # Transformers may return either:
        #   [frames, C, H, W]
        # or directly:
        #   [batch, frames, C, H, W]
        # The installed X-CLIP processor currently returns the latter.
        image_inputs = self.processor(
            images=frames,
            return_tensors="pt",
        )

        pixel_values = image_inputs["pixel_values"]

        if pixel_values.ndim == 4:
            # [frames, C, H, W] -> [1, frames, C, H, W]
            pixel_values = pixel_values.unsqueeze(0)
        elif pixel_values.ndim == 5:
            # Already [batch, frames, C, H, W].
            pass
        else:
            raise RuntimeError(
                "Unexpected X-CLIP pixel tensor shape: "
                f"{tuple(pixel_values.shape)}. Expected 4D or 5D."
            )

        # Ensure the temporal dimension matches the normalized clip.
        if pixel_values.shape[1] != self.num_frames:
            raise RuntimeError(
                "Unexpected X-CLIP frame count: "
                f"{pixel_values.shape[1]}. Expected {self.num_frames}."
            )

        pixel_values = pixel_values.to(
            device=self.device,
            dtype=self.model.dtype,
        )

        outputs = self.model(
            input_ids=self.text_inputs["input_ids"],
            attention_mask=self.text_inputs.get("attention_mask"),
            pixel_values=pixel_values,
        )

        probs = torch.softmax(
            outputs.logits_per_video[0],
            dim=-1,
        ).float().cpu().tolist()

        return dict(zip(self.labels, probs))
