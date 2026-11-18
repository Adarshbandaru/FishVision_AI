@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

for %%I in ("%~dp0.") do set "PROJECT_ROOT=%%~fI"

echo ======================================================================
echo                 FISHVISION AI PLATFORM [V2.4]
echo     Intelligent Marine Species Recognition and Multi-Model Benchmarks
echo ======================================================================
echo Project Root: "%PROJECT_ROOT%"
echo.

set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "CHECKPOINT_DIR=%PROJECT_ROOT%\checkpoints"
set "DATA_DIR=%PROJECT_ROOT%\data"
set "LOG_DIR=%PROJECT_ROOT%\logs"
set "RUNTIME_DIR=%LOG_DIR%\runtime"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"

:: --------------------------------------------------------------------------
:: PHASE 1: Validate Required Project Structure
:: --------------------------------------------------------------------------
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory missing: "%BACKEND_DIR%"
    echo Please verify that the extracted archive contains the backend folder.
    goto :FAIL
)

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory missing: "%FRONTEND_DIR%"
    echo Please verify that the extracted archive contains the frontend folder.
    goto :FAIL
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo [ERROR] Frontend configuration missing: "%FRONTEND_DIR%\package.json"
    goto :FAIL
)

if not exist "%DATA_DIR%" (
    echo [ERROR] Data directory missing: "%DATA_DIR%"
    goto :FAIL
)

if not exist "%DATA_DIR%\class_mapping.json" (
    echo [ERROR] Canonical class mapping missing: "%DATA_DIR%\class_mapping.json"
    goto :FAIL
)

if not exist "%CHECKPOINT_DIR%" (
    echo [ERROR] Checkpoints directory missing: "%CHECKPOINT_DIR%"
    goto :FAIL
)

:: --------------------------------------------------------------------------
:: PHASE 2: Validate Required Model Checkpoint Weights
:: --------------------------------------------------------------------------
set "MISSING_CKPT=0"
if not exist "%CHECKPOINT_DIR%\DINOv2_MasterBest_152.pth" (
    echo   [MISSING CHECKPOINT] DINOv2_MasterBest_152.pth
    set "MISSING_CKPT=1"
)
if not exist "%CHECKPOINT_DIR%\ViT_B16_V2_Best_152.pth" (
    echo   [MISSING CHECKPOINT] ViT_B16_V2_Best_152.pth
    set "MISSING_CKPT=1"
)
if not exist "%CHECKPOINT_DIR%\ConvNeXt_Tiny_Best_152.pth" (
    echo   [MISSING CHECKPOINT] ConvNeXt_Tiny_Best_152.pth
    set "MISSING_CKPT=1"
)
if not exist "%CHECKPOINT_DIR%\Swin_Tiny_Best_152.pth" (
    echo   [MISSING CHECKPOINT] Swin_Tiny_Best_152.pth
    set "MISSING_CKPT=1"
)
if not exist "%CHECKPOINT_DIR%\MobileNetV3_Best_152.pth" (
    echo   [MISSING CHECKPOINT] MobileNetV3_Best_152.pth
    set "MISSING_CKPT=1"
)

if "!MISSING_CKPT!"=="1" (
    echo.
    echo [ERROR] Required model weight checkpoint files are missing from:
    echo         "%CHECKPOINT_DIR%"
    echo Cannot proceed with offline multi-model inference.
    goto :FAIL
)

:: --------------------------------------------------------------------------
:: PHASE 3: Virtual Environment & Dependency Validation
:: --------------------------------------------------------------------------
set "NEED_SETUP=0"

if not exist "%PYTHON_EXE%" (
    echo [SETUP REQUIRED] Python virtual environment not found in: "%VENV_DIR%"
    set "NEED_SETUP=1"
) else (
    "%PYTHON_EXE%" -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo [SETUP REQUIRED] Python virtual environment is invalid for this machine.
        echo                 ^(Likely moved from another directory, drive, or user account^).
        set "NEED_SETUP=1"
    )
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [SETUP REQUIRED] Frontend dependencies not found in: "%FRONTEND_DIR%\node_modules"
    set "NEED_SETUP=1"
)

if "!NEED_SETUP!"=="1" (
    echo.
    echo Launching FIRST_TIME_SETUP.bat to configure the environment...
    echo.
    call "%PROJECT_ROOT%\FIRST_TIME_SETUP.bat"
    if errorlevel 1 (
        echo.
        echo [ERROR] First-time setup failed. Cannot launch application.
        goto :FAIL
    )
)

:: Final pre-flight verification after setup
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable still missing after setup: "%PYTHON_EXE%"
    goto :FAIL
)

"%PYTHON_EXE%" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python executable in .venv cannot be executed.
    goto :FAIL
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [ERROR] Frontend dependencies missing after setup.
    goto :FAIL
)

:: Ensure .env exists from template
if not exist "%PROJECT_ROOT%\.env" (
    if exist "%PROJECT_ROOT%\.env.example" (
        copy "%PROJECT_ROOT%\.env.example" "%PROJECT_ROOT%\.env" >nul
        echo Created default .env configuration.
    )
)

:: --------------------------------------------------------------------------
:: PHASE 4: Dynamic Port Allocation (Backend 8000-8004, Frontend 5173-5177)
:: --------------------------------------------------------------------------
echo [PORTS] Resolving dynamic ports for Backend and Frontend...
set "BACKEND_PORT="
set "BACKEND_ACTION="
set "FRONTEND_PORT="
set "FRONTEND_ACTION="

if exist "%RUNTIME_DIR%\set_ports.bat" del /f /q "%RUNTIME_DIR%\set_ports.bat" >nul 2>&1

"%PYTHON_EXE%" "%PROJECT_ROOT%\tools\port_manager.py" allocate
if errorlevel 1 (
    echo.
    echo [ERROR] Port allocation failed. Cannot proceed.
    goto :FAIL
)

if exist "%RUNTIME_DIR%\set_ports.bat" (
    call "%RUNTIME_DIR%\set_ports.bat"
)

if "!BACKEND_PORT!"=="" (
    echo.
    echo [ERROR] Failed to allocate an available backend port.
    echo Candidate ports [8000, 8001, 8002, 8003, 8004] are all occupied.
    goto :FAIL
)

if "!FRONTEND_PORT!"=="" (
    echo.
    echo [ERROR] Failed to allocate an available frontend port.
    echo Candidate ports [5173, 5174, 5175, 5176, 5177] are all occupied.
    goto :FAIL
)

echo         Backend Port:  !BACKEND_PORT! [!BACKEND_ACTION!]
echo         Frontend Port: !FRONTEND_PORT! [!FRONTEND_ACTION!]
echo.

:: --------------------------------------------------------------------------
:: PHASE 5: Start Backend API Service
:: --------------------------------------------------------------------------
if "!BACKEND_ACTION!"=="REUSE" (
    echo [1/2] Port !BACKEND_PORT! is running healthy FishVision backend. Reusing existing instance.
) else (
    echo [1/2] Starting FastAPI backend on http://127.0.0.1:!BACKEND_PORT! ...
    start "FishVision Backend API" /d "%PROJECT_ROOT%" /min cmd /c ""%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port !BACKEND_PORT! > "%LOG_DIR%\backend.log" 2>&1"
    "%PYTHON_EXE%" "%PROJECT_ROOT%\tools\port_manager.py" record-pid --service backend --port !BACKEND_PORT! >nul 2>&1
)

:: --------------------------------------------------------------------------
:: PHASE 6: Start Frontend Vite UI Service
:: --------------------------------------------------------------------------
set "VITE_BACKEND_PORT=!BACKEND_PORT!"
set "BACKEND_PORT=!BACKEND_PORT!"
set "VITE_PORT=!FRONTEND_PORT!"
set "PORT=!FRONTEND_PORT!"

if "!FRONTEND_ACTION!"=="REUSE" (
    echo [2/2] Port !FRONTEND_PORT! is running healthy FishVision frontend. Reusing existing instance.
) else (
    echo [2/2] Starting React + Vite frontend on http://127.0.0.1:!FRONTEND_PORT! ...
    start "FishVision React UI" /d "%FRONTEND_DIR%" /min cmd /c "npm run dev -- --port !FRONTEND_PORT! --host 127.0.0.1 > "%LOG_DIR%\frontend.log" 2>&1"
    "%PYTHON_EXE%" "%PROJECT_ROOT%\tools\port_manager.py" record-pid --service frontend --port !FRONTEND_PORT! >nul 2>&1
)

:: --------------------------------------------------------------------------
:: PHASE 7: Dynamic Readiness Health Polling
:: --------------------------------------------------------------------------
echo.
"%PYTHON_EXE%" "%PROJECT_ROOT%\tools\check_readiness.py" --backend-port !BACKEND_PORT! --frontend-port !FRONTEND_PORT!
if errorlevel 1 (
    echo.
    echo [ERROR] Services did not become healthy within the timeout window.
    echo Please inspect diagnostic logs for details:
    echo   - Backend:  "%LOG_DIR%\backend.log"
    echo   - Frontend: "%LOG_DIR%\frontend.log"
    echo.
    goto :FAIL
)

echo.
echo ======================================================================
echo   FishVision AI is live!
echo.
echo   Frontend [React + Vite]:  http://localhost:!FRONTEND_PORT!
echo   Backend API [FastAPI]:    http://localhost:!BACKEND_PORT!
echo   API Documentation:        http://localhost:!BACKEND_PORT!/docs
echo   Runtime Configuration:    "%RUNTIME_DIR%\runtime.json"
echo   Logs Directory:           "%LOG_DIR%"
echo ======================================================================
echo.

if not "%1"=="--no-browser" if not "%2"=="--no-browser" (
    start http://localhost:!FRONTEND_PORT!
)

echo Run 'stop.bat' anytime to shutdown background servers.
echo.
if not "%1"=="--no-pause" if not "%2"=="--no-pause" pause
exit /b 0

:FAIL
echo ======================================================================
echo Launcher aborted due to the error above.
echo ======================================================================
if not "%1"=="--no-pause" if not "%2"=="--no-pause" pause
exit /b 1
