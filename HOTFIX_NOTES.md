# v0.3.1 HOTFIX5

Fixed the actual issues reported from HOTFIX4.

## 1. IndentationError
The previous `main.py` contained an invalid indentation introduced while
normalizing quoted video paths. This has been corrected.

## 2. Video path with quotes
START.bat now removes all user-entered `"` characters before passing the path
to Python. Both forms are supported:

C:\Videos\Movie.mp4
"C:\Videos\Movie.mp4"

The batch file also validates that the file exists before starting the AI
pipeline.

## 3. FFmpeg / FFprobe
The project now checks bundled local binaries first, then Windows PATH.
The installer diagnostic copies FFmpeg/FFprobe from PATH into the project's
runtime folder when available.

## 4. Runtime diagnostic
Added TEST_RUNTIME.bat to verify FFmpeg/FFprobe and the Python environment
without processing a video.

No detection/decision thresholds or AI pipeline logic were intentionally
changed in this hotfix.
