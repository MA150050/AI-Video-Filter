@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title AI Video Filter v0.3.1

cls
echo.
echo  ==============================================================
echo                    AI VIDEO FILTER v0.3.1
echo  ==============================================================
echo.
echo                  MOHAMED ABD EL-HAFEZ
echo.
echo  --------------------------------------------------------------
echo  Offline AI video content filtering pipeline
echo  NSFW + X-CLIP + YOLO/ByteTrack + Temporal Analysis
echo  --------------------------------------------------------------
echo.

if not exist ".venv\Scripts\python.exe" (
    echo  [ERROR] Installation not found.
    echo  Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

set "VIDEO="
set /p "VIDEO=  Video path: "

if not defined VIDEO (
    echo.
    echo  No video path entered.
    pause
    exit /b 0
)

rem Remove surrounding quotes entered by the user.
rem This allows both:
rem   C:\Folder\Movie.mp4
rem   "C:\Folder\Movie.mp4"
set "VIDEO=%VIDEO:"=%"

if not exist "%VIDEO%" (
    echo.
    echo  [ERROR] Video file not found:
    echo  %VIDEO%
    echo.
    pause
    exit /b 1
)

echo.
echo  --------------------------------------------------------------
echo  Processing...
echo  --------------------------------------------------------------
echo.

".venv\Scripts\python.exe" -m app.main --video "%VIDEO%"
set "ERR=%ERRORLEVEL%"

echo.
echo  ==============================================================
if "%ERR%"=="0" (
    echo                         COMPLETE
) else (
    echo                       FAILED - %ERR%
)
echo  ==============================================================
echo.
echo  Copyright (c) 2026 MOHAMED ABD EL-HAFEZ
echo.
pause
exit /b %ERR%
