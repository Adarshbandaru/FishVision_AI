@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

for %%I in ("%~dp0.") do set "PROJECT_ROOT=%%~fI"

echo ======================================================================
echo                 FISHVISION AI PLATFORM - SHUTDOWN
echo ======================================================================
echo Project Root: "%PROJECT_ROOT%"
echo.

set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "RUNTIME_DIR=%PROJECT_ROOT%\logs\runtime"

if exist "%PYTHON_EXE%" if exist "%PROJECT_ROOT%\tools\port_manager.py" (
    "%PYTHON_EXE%" "%PROJECT_ROOT%\tools\port_manager.py" stop
    goto :DONE
)

:: Fallback if Python environment is unavailable
echo Terminating tracked FishVision services via PID files...
set "STOPPED_COUNT=0"

if exist "%RUNTIME_DIR%\backend.pid" (
    set /p BACKEND_PID=<"%RUNTIME_DIR%\backend.pid"
    if not "!BACKEND_PID!"=="" (
        echo   Terminating backend process [PID: !BACKEND_PID!]...
        taskkill /F /T /PID !BACKEND_PID! >nul 2>&1
        del /f /q "%RUNTIME_DIR%\backend.pid" >nul 2>&1
        set /a STOPPED_COUNT+=1
    )
)

if exist "%RUNTIME_DIR%\frontend.pid" (
    set /p FRONTEND_PID=<"%RUNTIME_DIR%\frontend.pid"
    if not "!FRONTEND_PID!"=="" (
        echo   Terminating frontend process [PID: !FRONTEND_PID!]...
        taskkill /F /T /PID !FRONTEND_PID! >nul 2>&1
        del /f /q "%RUNTIME_DIR%\frontend.pid" >nul 2>&1
        set /a STOPPED_COUNT+=1
    )
)

echo.
if !STOPPED_COUNT! gtr 0 (
    echo [SUCCESS] !STOPPED_COUNT! FishVision AI service process[es] terminated.
) else (
    echo [INFO] No active FishVision AI services were running [already stopped].
)

:DONE
echo ======================================================================
if not "%1"=="--no-pause" pause
exit /b 0
