@echo off
setlocal
cd /d "%~dp0"
title AI Video Filter - X-CLIP Test

if not exist ".venv\Scripts\python.exe" (
    echo Run INSTALL.bat first.
    pause
    exit /b 1
)

set "HF_HUB_OFFLINE=1"
set "TRANSFORMERS_OFFLINE=1"
set "YOLO_AUTOINSTALL=false"

".venv\Scripts\python.exe" app\test_xclip.py
echo.
pause
