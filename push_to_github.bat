@echo off
title Push VIRALCUT AI to GitHub
color 0A
cd /d "%~dp0"
echo =====================================================================
echo    Pushing VIRALCUT AI Studio to GitHub
echo    Target: https://github.com/sajidalikhan033586-dot/viralcut-ai.git
echo =====================================================================
echo.
echo If a GitHub sign-in window pops up, click "Sign in with your browser"
echo.
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo  [+] SUCCESS! Your project has been uploaded to GitHub!
    echo  [+] View repo: https://github.com/sajidalikhan033586-dot/viralcut-ai
    echo =====================================================================
) else (
    echo.
    echo [!] Push failed or authorization was cancelled.
)
pause
