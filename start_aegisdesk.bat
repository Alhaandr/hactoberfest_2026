@echo off
setlocal
echo ========================================================
echo        AEGISDESK - Air-Gapped Forensic Investigator
echo ========================================================
echo [1/3] Setting local environment paths...
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\AppData\Local\Programs\Ollama;%PATH%"

echo [2/3] Checking Ollama local server...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama background daemon is active.
) else (
    echo [INFO] Starting headless Ollama daemon...
    start /B "" "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
)

echo [3/3] Launching AegisDesk Forensic Application...
start http://127.0.0.1:8000
"%~dp0backend\.venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause

