@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

for %%I in ("%~dp0.") do set "PROJECT_ROOT=%%~fI"

set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "CHECKPOINT_DIR=%PROJECT_ROOT%\checkpoints"
set "DATA_DIR=%PROJECT_ROOT%\data"
set "LOG_DIR=%PROJECT_ROOT%\logs"
set "SETUP_LOG=%LOG_DIR%\setup.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ======================================================================
echo                FISHVISION AI -- FIRST-TIME ENVIRONMENT SETUP
echo ======================================================================
echo Project Root: "%PROJECT_ROOT%"
echo Logging to:   "%SETUP_LOG%"
echo.

echo ====================================================================== > "%SETUP_LOG%"
echo FishVision AI Setup Log - %DATE% %TIME% >> "%SETUP_LOG%"
echo ====================================================================== >> "%SETUP_LOG%"

echo [1/8] Detecting Windows Environment and Package Manager...
echo [1/8] Detecting Windows Environment and Package Manager... >> "%SETUP_LOG%"

for /f "tokens=*" %%a in ('ver') do (
    echo       OS: %%a
    echo OS: %%a >> "%SETUP_LOG%"
)

set "HAS_WINGET=0"
where winget >nul 2>&1
if not errorlevel 1 (
    set "HAS_WINGET=1"
    echo       Windows Package Manager [winget]: Available
    echo Windows Package Manager: Available >> "%SETUP_LOG%"
) else (
    echo       Windows Package Manager [winget]: Not found
    echo Windows Package Manager: Not found >> "%SETUP_LOG%"
)

echo.
echo [2/8] Detecting Python Runtime [Python 3.10-3.12]...
echo [2/8] Detecting Python Runtime... >> "%SETUP_LOG%"

REM Refresh environment path from registry if possible
for /f "tokens=2*" %%a in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USR_PATH=%%b"
set "PATH=%SYS_PATH%;%USR_PATH%;%PATH%"
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
if exist "%ProgramFiles%\Python312\python.exe" set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
if exist "%ProgramFiles%\nodejs\node.exe" set "PATH=%ProgramFiles%\nodejs;%PATH%"

set "PYTHON_SYSTEM="

py -3.12 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_SYSTEM=py -3.12"

if "!PYTHON_SYSTEM!"=="" (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_SYSTEM=py -3"
)

if "!PYTHON_SYSTEM!"=="" (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_SYSTEM=python"
)

if "!PYTHON_SYSTEM!"=="" (
    if "!HAS_WINGET!"=="1" (
        echo       Python not detected. Attempting automated install via winget...
        echo       Executing: winget install --id Python.Python.3.12 -e ...
        winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements >> "%SETUP_LOG%" 2>&1
        if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
        if exist "%ProgramFiles%\Python312\python.exe" set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
        python --version >nul 2>&1
        if not errorlevel 1 set "PYTHON_SYSTEM=python"
    )
)

if "!PYTHON_SYSTEM!"=="" (
    echo.
    echo ======================================================================
    echo ERROR: Python 3.10-3.12 is required but could not be located.
    echo.
    echo Please install Python 3.12 from:
    echo   https://www.python.org/downloads/release/python-3128/
    echo.
    echo IMPORTANT: During installation, check:
    echo   [x] "Add python.exe to PATH"
    echo ======================================================================
    echo ERROR: Python missing >> "%SETUP_LOG%"
    if not "%1"=="--no-pause" pause
    exit /b 1
)

for /f "tokens=*" %%v in ('!PYTHON_SYSTEM! --version 2^>^&1') do (
    echo       Found: %%v [!PYTHON_SYSTEM!]
    echo Python Version: %%v >> "%SETUP_LOG%"
)

echo.
echo [3/8] Detecting Node.js and npm [Node LTS]...
echo [3/8] Detecting Node.js and npm... >> "%SETUP_LOG%"

set "HAS_NODE=0"
node --version >nul 2>&1
if not errorlevel 1 set "HAS_NODE=1"

if "!HAS_NODE!"=="0" (
    if "!HAS_WINGET!"=="1" (
        echo       Node.js not detected. Attempting automated install via winget...
        echo       Executing: winget install --id OpenJS.NodeJS.LTS -e ...
        winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements >> "%SETUP_LOG%" 2>&1
        if exist "%ProgramFiles%\nodejs\node.exe" set "PATH=%ProgramFiles%\nodejs;%PATH%"
        node --version >nul 2>&1
        if not errorlevel 1 set "HAS_NODE=1"
    )
)

if "!HAS_NODE!"=="0" (
    echo.
    echo ======================================================================
    echo ERROR: Node.js [LTS] is required for the React frontend.
    echo.
    echo Please download and install Node.js LTS from:
    echo   https://nodejs.org/
    echo ======================================================================
    echo ERROR: Node.js missing >> "%SETUP_LOG%"
    if not "%1"=="--no-pause" pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version') do echo       Node.js: %%v
for /f "tokens=*" %%v in ('npm --version') do echo       npm:     %%v
node --version >> "%SETUP_LOG%"
call npm --version >> "%SETUP_LOG%"

echo.
echo [4/8] Setting up Python virtual environment [.venv]...
echo [4/8] Setting up Python virtual environment [.venv]... >> "%SETUP_LOG%"

REM Validate whether existing .venv is executable on THIS system
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo       Existing .venv is invalid or was created for a different machine.
        echo       Rebuilding fresh virtual environment...
        rmdir /s /q "%VENV_DIR%" >> "%SETUP_LOG%" 2>&1
    )
)

if not exist "%PYTHON_EXE%" (
    echo       Creating clean virtual environment in .venv ...
    !PYTHON_SYSTEM! -m venv "%VENV_DIR%" >> "%SETUP_LOG%" 2>&1
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. See logs\setup.log.
        if not "%1"=="--no-pause" pause
        exit /b 1
    )
    echo       Virtual environment created successfully.
) else (
    echo       Virtual environment [.venv] is valid. Reusing.
)

echo.
echo [5/8] Installing Python backend dependencies [requirements.txt]...
echo [5/8] Installing Python backend dependencies... >> "%SETUP_LOG%"

echo       Upgrading pip...
"%PYTHON_EXE%" -m pip install -q --upgrade pip >> "%SETUP_LOG%" 2>&1

echo       Installing packages from requirements.txt...
"%PYTHON_EXE%" -m pip install -q -r "%PROJECT_ROOT%\requirements.txt" >> "%SETUP_LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies. See logs\setup.log.
    if not "%1"=="--no-pause" pause
    exit /b 1
)
echo       Python backend dependencies installed successfully.

echo.
echo [6/8] Installing React + Vite frontend dependencies...
echo [6/8] Installing React + Vite frontend dependencies... >> "%SETUP_LOG%"

cd /d "%FRONTEND_DIR%"

if not exist "node_modules" (
    echo       Running npm ci [clean install from package-lock.json]...
    call npm ci >> "%SETUP_LOG%" 2>&1
    if errorlevel 1 (
        echo       npm ci failed; retrying with npm install...
        call npm install >> "%SETUP_LOG%" 2>&1
        if errorlevel 1 (
            echo ERROR: Failed to install frontend dependencies. See logs\setup.log.
            cd /d "%PROJECT_ROOT%"
            if not "%1"=="--no-pause" pause
            exit /b 1
        )
    )
    echo       Frontend packages installed successfully.
) else (
    echo       Frontend node_modules already exists. Skipping reinstall.
)
cd /d "%PROJECT_ROOT%"

echo.
echo [7/8] Verifying model checkpoints and neural backbones...
echo [7/8] Verifying model checkpoints... >> "%SETUP_LOG%"

"%PYTHON_EXE%" "%PROJECT_ROOT%\tools\verify_setup.py"
if errorlevel 1 (
    echo ERROR: Model verification failed. See details above.
    if not "%1"=="--no-pause" pause
    exit /b 1
)

echo.
echo [8/8] Validating React + Vite frontend production build...
echo [8/8] Validating React + Vite frontend production build... >> "%SETUP_LOG%"

cd /d "%FRONTEND_DIR%"
call npm run build >> "%SETUP_LOG%" 2>&1
if errorlevel 1 (
    echo ERROR: Frontend build validation failed. See logs\setup.log.
    cd /d "%PROJECT_ROOT%"
    if not "%1"=="--no-pause" pause
    exit /b 1
)
echo       Production bundle compiled cleanly [dist/ generated].
cd /d "%PROJECT_ROOT%"

echo.
echo ======================================================================
echo               FIRST-TIME SETUP COMPLETED SUCCESSFULLY!
echo ======================================================================
echo.
echo The FishVision AI Platform is fully configured and ready to run.
echo.
echo To launch the application:
echo   Double-click:  run.bat
echo.
echo To stop background servers:
echo   Double-click:  stop.bat
echo ======================================================================

echo Setup status: SUCCESS >> "%SETUP_LOG%"
if not "%1"=="--no-pause" pause
exit /b 0
