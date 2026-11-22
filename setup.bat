@echo off
title VIRALCUT AI - Automatic Studio Setup
color 0B

echo ===============================================================================
echo     VIRALCUT AI - Autonomous Short-Form Video Clipping Studio
echo                   One-Click Automatic Environment Setup
echo ===============================================================================
echo.
cd /d "%~dp0"

:: 1. DETECT OR INSTALL PYTHON
echo [*] Step 1/5: Checking Python installation...
set PYTHON_CMD=

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :PYTHON_FOUND
)

py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3
    goto :PYTHON_FOUND
)

if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD="%LocalAppData%\Programs\Python\Python312\python.exe"
    goto :PYTHON_FOUND
)
if exist "%LocalAppData%\Programs\Python\Python315\python.exe" (
    set PYTHON_CMD="%LocalAppData%\Programs\Python\Python315\python.exe"
    goto :PYTHON_FOUND
)
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD="%LocalAppData%\Programs\Python\Python311\python.exe"
    goto :PYTHON_FOUND
)

echo [!] Python was not detected in PATH.
echo [*] Attempting automatic Python installation via Windows Package Manager (winget)...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if %ERRORLEVEL% EQU 0 (
    echo [+] Python installed successfully! Please restart this setup window.
    pause
    exit /b 0
)

echo.
echo [ERROR] Python 3.10+ is required to run VIRALCUT AI.
echo Please download and install Python from: https://www.python.org/downloads/
echo (IMPORTANT: Make sure to check the box "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [+] Python detected:
%PYTHON_CMD% --version
echo.

:: 2. DETECT OR INSTALL FFMPEG
echo [*] Step 2/5: Checking FFmpeg multimedia processor...
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [+] FFmpeg is installed and accessible in PATH.
) else (
    echo [!] FFmpeg is not found in PATH.
    echo [*] Attempting automatic FFmpeg installation via winget...
    winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if %ERRORLEVEL% EQU 0 (
        echo [+] FFmpeg installed successfully!
    ) else (
        echo [NOTE] If video rendering shows errors later, install FFmpeg via 'winget install Gyan.FFmpeg'.
    )
)
echo.

:: 3. CREATE VIRTUAL ENVIRONMENT
echo [*] Step 3/5: Setting up isolated Python virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [+] Virtual environment created successfully.
) else (
    echo [+] Existing virtual environment detected.
)
echo.

:: 4. INSTALL DEPENDENCIES
echo [*] Step 4/5: Installing and verifying AI libraries (Whisper, PyTorch, FastAPI, OpenCV)...
echo [*] Upgrading pip package installer...
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q

echo [*] Installing requirements from requirements.txt...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Some packages failed to install. Please check your internet connection.
    pause
    exit /b 1
)
echo [+] All dependencies installed and verified successfully!
echo.

:: 5. CREATE DESKTOP SHORTCUT
echo [*] Step 5/5: Creating one-click Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $d = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'VIRALCUT AI Studio.lnk'); $s = $ws.CreateShortcut($d); $s.TargetPath = [System.IO.Path]::Combine('%~dp0', 'start.bat'); $s.WorkingDirectory = '%~dp0'; $s.Description = 'VIRALCUT AI - Autonomous Short-Form Video Clipping Studio'; $s.Save()"
if exist "%UserProfile%\Desktop\VIRALCUT AI Studio.lnk" (
    echo [+] Shortcut 'VIRALCUT AI Studio' created on your Desktop!
) else (
    echo [NOTE] You can launch the studio anytime by double-clicking 'start.bat'.
)
echo.

:: VERIFICATION CHECK
echo [*] Running system diagnostic validation...
.\.venv\Scripts\python.exe -c "import fastapi, uvicorn, whisper, cv2, torch; print('    [OK] FastAPI, Whisper STT, OpenCV, PyTorch engines loaded cleanly!')"
echo.

echo ===============================================================================
echo   CONGRATULATIONS! VIRALCUT AI STUDIO IS FULLY CONFIGURED AND READY TO USE!
echo ===============================================================================
echo.
echo   You can launch the studio now, or launch it later from the Desktop shortcut.
echo.
set /p LAUNCH_CHOICE="Do you want to launch the studio right now? (Y/N): "
if /i "%LAUNCH_CHOICE%"=="Y" (
    echo.
    echo [*] Launching studio...
    start start.bat
) else (
    echo.
    echo [+] Setup finished. Double-click 'VIRALCUT AI Studio' on your Desktop whenever you want to use it.
    pause
)
