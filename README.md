# AI Video Filter v0.3.1 HOTFIX

Accuracy-focused upgrade:
- NSFW frame classification
- X-CLIP temporal semantic analysis
- YOLO26 person detection + ByteTrack persistence
- Person proximity / overlap / face-to-face heuristics
- Temporal voting
- Conservative intimate-hug confirmation
- Scene-based processing
- Resume state
- FFmpeg output
- JSON/TXT reports

The person tracker is supporting evidence only; it is not a sexual-content classifier. This reduces false positives from ordinary hugs but does not guarantee perfect classification.

Ultralytics documents YOLO tracking with ByteTrack/BoT-SORT and persistent tracks:
https://docs.ultralytics.com/modes/track

Hugging Face video classification overview:
https://huggingface.co/tasks/video-classification

X-CLIP:
https://huggingface.co/microsoft/xclip-base-patch16

NSFW classifier:
https://huggingface.co/viddexa/nsfw-detection-2-mini

PySceneDetect:
https://www.scenedetect.com/

FFmpeg:
https://ffmpeg.org/


## Copyright

**Copyright © 2026 MOHAMED ABD EL-HAFEZ**  
[Contact](https://www.facebook.com/profile.php?id=100078064892942)
