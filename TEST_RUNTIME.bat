@echo off
setlocal
cd /d "%~dp0"
title AI Video Filter - Runtime Test

if not exist ".venv\Scripts\python.exe" (
    echo Run INSTALL.bat first.
    pause
    exit /b 1
)

set "HF_HUB_OFFLINE=1"
set "TRANSFORMERS_OFFLINE=1"
set "YOLO_AUTOINSTALL=false"

".venv\Scripts\python.exe" app\check_ffmpeg.py
if errorlevel 1 (
    echo.
    echo FFmpeg test FAILED.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" app\test_environment.py

echo.
echo Runtime test completed.
pause
