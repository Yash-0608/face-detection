@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo        FaceVision AI - Windows Launcher
echo ==========================================
echo Project folder: %CD%
echo.

if not exist "backend\app.py" (
  echo ERROR: backend\app.py was not found.
  echo Download or clone the complete face-detection repository,
  echo then run this file from its root folder.
  pause
  exit /b 1
)

if not exist "model\best.pt" (
  echo ERROR: model\best.pt is missing.
  echo The detector cannot start without the trained model.
  pause
  exit /b 1
)

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python launcher "py" was not found. Install Python 3.10-3.12.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating project virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Python 3.11 was not found. Trying the default Python installation...
    py -m venv .venv
    if errorlevel 1 (
      echo ERROR: Could not create virtual environment.
      pause
      exit /b 1
    )
  )
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo.
echo Starting FaceVision from the correct repository directory...
echo Open http://127.0.0.1:5000/workspace in your browser.
echo Keep this window open while using the application.
echo If port 5000 is already in use, stop the older Python server first.
echo.
".venv\Scripts\python.exe" backend\app.py
if errorlevel 1 goto :failed
goto :end

:failed
echo.
echo Startup failed. Read the error above.
pause
exit /b 1

:end
endlocal
