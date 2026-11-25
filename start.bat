@echo off
title NextRise Clipper AI - Autonomous Short-Form Video Studio
color 0B
cd /d "%~dp0"

if not exist ".\.venv\Scripts\python.exe" (
    echo =====================================================================
    echo  [!] First-time setup detected. Running automated environment setup...
    echo =====================================================================
    echo.
    call setup.bat
    exit /b 0
)

echo =====================================================================
echo    NextRise Clipper AI - Autonomous Short-Form Video Studio
echo             Powered by NextRise Digital (nextrisehq.com)
echo =====================================================================
echo.
echo  [+] Launching local AI backend...
echo  [+] Models loaded: Whisper STT, OpenCV Smart Reframer, 9:16 Video Engine
echo  [+] Studio URL: http://127.0.0.1:8000
echo.
echo  Please wait... Your browser will open automatically in 2-3 seconds!
echo  (Keep this black window open in the background while using the app)
echo =====================================================================
echo.
.\.venv\Scripts\python.exe run_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server encountered an error. Press any key to exit.
    pause
)
