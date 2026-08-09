from pathlib import Path
import sys
import logging
import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.xclip_detector import XClipDetector


def main():
    cfg = yaml.safe_load(
        (ROOT / "config" / "config.yaml").read_text(encoding="utf-8")
    )

    logger = logging.getLogger("xclip_test")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
        logger.addHandler(handler)

    detector = XClipDetector(cfg, ROOT, logger)

    # Synthetic RGB clip: 8 frames, matching the X-CLIP checkpoint.
    frames = [
        np.zeros((224, 224, 3), dtype=np.uint8)
        for _ in range(8)
    ]

    print("Input frames:", len(frames), "shape:", frames[0].shape)
    scores = detector.score_clip(frames)

    print()
    print("=" * 60)
    print("X-CLIP TEST: OK")
    print("=" * 60)
    print("Device:", detector.device)
    print("PyTorch:", torch.__version__)
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
    print("Top scores:")
    for label, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {label}: {score:.4f}")


if __name__ == "__main__":
    main()
