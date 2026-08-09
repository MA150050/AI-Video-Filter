# AI Video Filter

**AI Video Filter** is an offline AI-powered video filtering pipeline
for Windows that detects potentially unwanted intimate, sexual, and nude
scenes in local videos and removes the detected time ranges.

**Current release:** `v0.3.1-HOTFIX5`

> Experimental project. Detection is not guaranteed to be perfect.

------------------------------------------------------------------------

## Features

-   NSFW frame-level classification
-   **X-CLIP** temporal video-text analysis
-   **YOLO26** person detection
-   **ByteTrack** multi-person tracking
-   Person proximity / interaction heuristics
-   Temporal evidence filtering
-   PySceneDetect scene segmentation
-   Automatic detection-range buffering and merging
-   FFmpeg video reconstruction
-   Resume/progress state
-   JSON and TXT detection reports
-   Local/offline inference after installation

The person tracker is **supporting evidence only**, not a standalone
sexual-content classifier.

------------------------------------------------------------------------

## Pipeline

``` text
Input Video
    │
    ▼
PySceneDetect
    │
    ▼
Frame Sampling
    ├──► NSFW Classification
    └──► YOLO26 + ByteTrack
                 │
                 ▼
        Interaction Heuristics
                 │
    ┌────────────┘
    ▼
X-CLIP Temporal Analysis
    │
    ▼
Decision Fusion + Temporal Verification
    │
    ▼
Buffer Expansion + Range Merging
    │
    ▼
FFmpeg Reconstruction
    │
    ▼
Clean Video + Reports
```

------------------------------------------------------------------------

# Installation

## Requirements

-   Windows 10 / 11 x64
-   **Python 3.11 or 3.12 x64**
-   NVIDIA CUDA GPU strongly recommended
-   FFmpeg + FFprobe
-   Internet connection for initial package/model downloads

Verify Python:

``` bat
python --version
```

Verify FFmpeg:

``` bat
ffmpeg -version
ffprobe -version
```

The project creates its own `.venv`, so dependencies do not need to be
installed globally.

------------------------------------------------------------------------

## 1. Download

Clone the repository:

``` bat
git clone https://github.com/MA150050/AI-Video-Filter.git
cd AI-Video-Filter
```

Or download the repository ZIP and extract it.

------------------------------------------------------------------------

## 2. Install

Run:

``` bat
INSTALL.bat
```

The installer:

1.  Creates `.venv`
2.  Installs/upgrades Python dependencies
3.  Installs the configured PyTorch build
4.  Downloads required AI models
5.  Checks FFmpeg / FFprobe
6.  Tests the local runtime

Models are stored locally under:

``` text
models\
```

They are intentionally excluded from GitHub.

> Initial installation requires Internet access. Normal inference is
> designed to run locally afterward.

------------------------------------------------------------------------

## 3. Verify the Installation

Run:

``` bat
TEST_RUNTIME.bat
```

This checks:

-   Python / PyTorch
-   CUDA and NVIDIA GPU
-   VRAM
-   NSFW model
-   X-CLIP
-   YOLO26
-   FFmpeg / FFprobe

For X-CLIP specifically:

``` bat
TEST_XCLIP.bat
```

A successful X-CLIP test should end with:

``` text
X-CLIP TEST: OK
```

------------------------------------------------------------------------

# Usage

## Quick Start

Run:

``` bat
START.bat
```

Enter the full video path when prompted:

``` text
C:\Videos\Movie.mp4
```

Quoted paths are supported:

``` text
"C:\Videos\My Movie.mp4"
```

The original video is not modified.

------------------------------------------------------------------------

## Direct Python Usage

The pipeline can also be started directly:

``` bat
.venv\Scripts\python.exe -m app.main --video "C:\Videos\Movie.mp4"
```

This is useful for automation and debugging.

------------------------------------------------------------------------

# Processing

For each video, the pipeline:

### 1. Detects Scenes

PySceneDetect separates the video into scenes so that analysis can be
performed independently.

### 2. Samples Frames

Frames are sampled for NSFW classification and person analysis.

### 3. Runs NSFW Classification

The current NSFW model detects classes including:

``` text
Normal
Porn
Hentai
Drawing
Sexy
```

### 4. Detects and Tracks People

YOLO26 detects people and ByteTrack maintains their identities across
frames.

Supporting signals include:

-   number of people
-   proximity
-   bounding-box overlap
-   interaction score
-   face-to-face interaction

### 5. Runs X-CLIP

X-CLIP evaluates temporal clips against semantic labels such as:

``` text
two people kissing
two people making out
two people hugging intimately
a sexual or intimate scene
a nude scene
a romantic but non-intimate scene
people talking
people walking
people fighting
```

Current X-CLIP sampling:

``` text
Frames per clip: 8
Clip duration:    4 seconds
Stride:           2 seconds
```

### 6. Combines Evidence

NSFW, X-CLIP, person interaction, and temporal evidence are combined by
the decision engine.

Selected semantic detections require temporal evidence instead of
relying on a single isolated observation.

### 7. Expands and Merges Ranges

Default removal buffer:

``` text
Before: 4 seconds
After:  5 seconds
Merge gap: 1.5 seconds
```

### 8. Reconstructs the Video

FFmpeg removes the detected ranges and creates a new video containing
the remaining segments.

Default encoding:

``` text
Video:  libx264
Preset: medium
CRF:    18
Audio:  AAC 192k
```

------------------------------------------------------------------------

# Output

For:

``` text
Movie.mp4
```

the default output is:

``` text
output\Movie_Clean.mp4
```

Existing output files are not overwritten by default; a secondary name
such as:

``` text
Movie_Clean_2.mp4
```

may be created.

------------------------------------------------------------------------

# Reports and Resume

Reports are stored in:

``` text
logs\
```

They contain information such as:

-   input/output paths
-   duration
-   processing device
-   detected events
-   confidence scores
-   timestamps
-   final removed ranges

Both structured JSON and human-readable TXT reports may be generated.

Processing state is stored under:

``` text
temp\
```

For example:

``` text
temp\Movie.progress.json
```

If processing is interrupted, completed scene information can be reused.

To force a completely fresh analysis, remove the corresponding progress
file.

------------------------------------------------------------------------

# Configuration

Main configuration:

``` text
config\config.yaml
```

Important settings include:

``` yaml
runtime:
  device: "cuda"

sampling:
  nsfw_fps: 1.5
  tracking_fps: 3.0
  suspicious_tracking_fps: 6.0
  xclip_clip_seconds: 4.0
  xclip_stride_seconds: 2.0
  xclip_frames: 8
```

X-CLIP decision thresholds are configurable:

``` yaml
decision:
  xclip:
    kissing: 0.82
    making_out: 0.86
    intimate_hug: 0.88
    intimate_scene: 0.88
    nude_scene: 0.84
```

Removal buffers:

``` yaml
buffer:
  before_seconds: 4.0
  after_seconds: 5.0
  merge_gap_seconds: 1.5
```

Encoding:

``` yaml
encoding:
  video_codec: "libx264"
  preset: "medium"
  crf: 18
  audio_codec: "aac"
  audio_bitrate: "192k"
```

Higher sampling rates increase analysis time. Higher semantic thresholds
generally make detection more conservative.

------------------------------------------------------------------------

# Models & Dependencies

  Component                         Purpose
  --------------------------------- -----------------------------------
  `viddexa/nsfw-detection-2-mini`   Frame-level NSFW classification
  `microsoft/xclip-base-patch16`    Temporal video-text analysis
  YOLO26                            Person detection
  ByteTrack                         Person tracking
  PySceneDetect                     Scene detection
  FFmpeg                            Video analysis and reconstruction
  PyTorch                           Local AI inference
  Transformers                      Model loading/inference

Official references:

-   [X-CLIP](https://huggingface.co/microsoft/xclip-base-patch16)
-   [NSFW
    Detection](https://huggingface.co/viddexa/nsfw-detection-2-mini)
-   [Ultralytics YOLO](https://docs.ultralytics.com/)
-   [PySceneDetect](https://www.scenedetect.com/)
-   [FFmpeg](https://ffmpeg.org/)
-   [Hugging Face
    Transformers](https://huggingface.co/docs/transformers/)

------------------------------------------------------------------------

# Offline Operation

After the required packages and models have been downloaded, the
inference pipeline is designed to run locally.

No cloud AI API is required for normal inference.

The project uses local model files and can enable offline Hugging Face /
Transformers behavior during diagnostics.

> Internet access is still required for the initial installation and
> model downloads.

------------------------------------------------------------------------

# Performance

Processing speed depends on:

-   GPU and VRAM
-   CPU
-   video resolution and duration
-   number of scenes
-   sampling rates
-   number of detected people
-   X-CLIP workload
-   storage speed

For faster processing, tune the sampling and X-CLIP settings in:

``` text
config\config.yaml
```

Changing multiple thresholds at once is not recommended when tuning
accuracy.

------------------------------------------------------------------------

# Troubleshooting

### Python not found

Install Python 3.11/3.12 x64 and enable **Add Python to PATH**, then
open a new Command Prompt.

``` bat
python --version
```

### FFmpeg / FFprobe missing

Verify:

``` bat
ffmpeg -version
ffprobe -version
```

Install FFmpeg and add its `bin` directory to Windows `PATH`, then run
`INSTALL.bat` again.

### CUDA is unavailable

Run:

``` bat
TEST_RUNTIME.bat
```

If CUDA is unavailable, the application can fall back to CPU inference,
but performance will be lower.

### X-CLIP test fails

Run:

``` bat
TEST_XCLIP.bat
```

Then check:

1.  `models\xclip\` contains the model files.
2.  Installation completed successfully.
3.  PyTorch/CUDA is working.
4.  `.venv` exists.

### Installation/model download fails

Check Internet access, disk space, and rerun:

``` bat
INSTALL.bat
```

### Reprocess a video from scratch

Delete its progress file from:

``` text
temp\
```

and run the video again.

------------------------------------------------------------------------

# Project Structure

``` text
AI-Video-Filter/
├── app/
│   ├── main.py
│   ├── nsfw_detector.py
│   ├── xclip_detector.py
│   ├── person_tracker.py
│   ├── decision_engine.py
│   ├── scene_detector.py
│   ├── frame_sampler.py
│   ├── video_editor.py
│   ├── setup_models.py
│   ├── check_ffmpeg.py
│   ├── test_environment.py
│   ├── test_xclip.py
│   └── utils.py
├── config/
│   └── config.yaml
├── models/
├── input/
├── output/
├── temp/
├── logs/
├── INSTALL.bat
├── START.bat
├── TEST_RUNTIME.bat
├── TEST_XCLIP.bat
├── requirements.txt
├── README.md
├── HOTFIX_NOTES.md
├── COPYRIGHT.md
├── BRAND.txt
└── .gitignore
```

------------------------------------------------------------------------

# v0.3.1 HOTFIX5

This release includes reliability and runtime fixes over the previous
HOTFIX build.

### Fixed

-   Corrected an `IndentationError` in `main.py`
-   Improved quoted video-path handling
-   Added input-path validation
-   Improved FFmpeg / FFprobe detection
-   Added runtime diagnostics
-   Added a dedicated X-CLIP test
-   Preserved the existing detection thresholds and decision logic

See [HOTFIX_NOTES.md](HOTFIX_NOTES.md) for details.

------------------------------------------------------------------------

# Limitations

-   Windows-focused release
-   NVIDIA CUDA is strongly recommended
-   CPU inference is possible but slower
-   Initial installation requires Internet access
-   AI model weights are not stored in this repository
-   Detection can produce false positives and false negatives
-   Difficult lighting, occlusion, motion blur, camera angles, and rapid
    cuts can reduce accuracy
-   Output video is re-encoded by FFmpeg
-   Unusual video stream layouts may require additional FFmpeg handling

For important content-review workflows, detected ranges should be
manually reviewed.

------------------------------------------------------------------------

# Privacy

The intended processing workflow is local. After installation, video
frames are processed by local models rather than a remote AI API.

Users are responsible for ensuring they have the legal right to process
the videos they provide.

------------------------------------------------------------------------

# Third-Party Licensing

The project integrates third-party software and model weights. Always
review the current license/model-card terms before redistribution.

  Component              License / Terms
  ---------------------- -------------------------------------
  X-CLIP                 MIT
  NSFW Detection model   Apache-2.0
  PySceneDetect          BSD 3-Clause
  Ultralytics YOLO       AGPL-3.0 / Enterprise
  FFmpeg                 LGPL 2.1+ / optional GPL components
  PyTorch                See PyTorch license
  Transformers           See Hugging Face license

------------------------------------------------------------------------

# Copyright

**Copyright © 2026 MOHAMED ABD EL-HAFEZ**

See [COPYRIGHT.md](COPYRIGHT.md) for the project copyright notice and
terms.

------------------------------------------------------------------------

# Status

**Current release:** `v0.3.1-HOTFIX5`

The project is under active development.

Future work includes improved temporal verification, false-positive
suppression, performance/GPU-memory optimization, reporting, and
GUI-based review tools.
