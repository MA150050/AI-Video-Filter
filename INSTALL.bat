@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title AI Video Filter v0.3 - Installer

echo ============================================================
echo                 AI VIDEO FILTER v0.3
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found in PATH.
  echo Install Python 3.11 or 3.12 x64.
  pause
  exit /b 1
)

python --version

if not exist ".venv\Scripts\python.exe" (
  echo [1/7] Creating local environment...
  python -m venv .venv || goto :fail
) else (
  echo [1/7] Existing environment found.
)

set "PY=.venv\Scripts\python.exe"

echo [2/7] Upgrading pip...
"%PY%" -m pip install --upgrade pip wheel setuptools || goto :fail

echo [3/7] Installing PyTorch...
"%PY%" -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
if errorlevel 1 (
  echo CUDA wheel unavailable; trying PyPI...
  "%PY%" -m pip install torch torchvision || goto :fail
)

echo [4/7] Installing dependencies...
"%PY%" -m pip install -r requirements.txt || goto :fail

echo [5/7] Downloading AI models...
"%PY%" app\setup_models.py || goto :fail

echo [6/7] Checking FFmpeg...
"%PY%" app\check_ffmpeg.py || goto :fail

echo [7/7] Testing CUDA and models...
"%PY%" app\test_environment.py || goto :fail

echo.
echo ============================================================
echo INSTALLATION COMPLETE
echo ============================================================
echo Run START.bat
pause
exit /b 0

:fail
echo.
echo INSTALLATION FAILED.
pause
exit /b 1
