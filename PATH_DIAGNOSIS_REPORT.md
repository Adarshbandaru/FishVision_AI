# FishVision AI — Path Diagnosis & Launcher Failure Report

**Document Version:** 1.0  
**Audit Date:** November 11, 2026  
**Auditor:** Senior Windows DevOps & Full-Stack Deployment Specialist  
**Project Root:** `C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App`  

---

## 1. Original Failure Description

When the FishVision AI project ZIP archive was extracted onto another Windows laptop or into a non-default directory (such as a path containing spaces or a different drive), executing `run.bat` failed immediately with the following error displayed in both the backend and frontend terminal windows:

```text
The system cannot find the path specified.
```

As a consequence of this failure:
1. The FastAPI backend never started, leaving port 8000 unoccupied.
2. The React + Vite frontend never started, leaving port 5173 unoccupied.
3. The health readiness probe timed out after 30 seconds.
4. The application failed to open in the user's browser.

---

## 2. Root Cause Analysis

Our comprehensive static inspection and dynamic runtime tracing identified **four distinct root causes** contributing to the `The system cannot find the path specified` failure:

### Root Cause 1: Escaped Quote Syntax in `cmd /c` Caused by Trailing Backslashes
In the original `run.bat`, the dynamic project root was defined using:
```bat
set "PROJECT_ROOT=%~dp0"
```
In Windows batch scripting, `%~dp0` always evaluates with a trailing backslash (for example, `C:\Users\John Doe\Downloads\FishVision\`).

When the child process was launched:
```bat
start "FishVision Backend API" /min cmd /c "cd /d "%PROJECT_ROOT%" && call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > logs\backend.log 2>&1"
```
The expression `"%PROJECT_ROOT%"` expanded to `"C:\Users\John Doe\Downloads\FishVision\"`.
Under Windows argument escaping rules, a trailing backslash immediately preceding a double quotation mark (`\"`) is interpreted as an **escaped quote** rather than a closing delimiter. Consequently:
- `cmd.exe` saw an open quote that was never terminated before the `&&` operator.
- The command interpreter attempted to change directory to a mangled path: `cd /d "C:\Users\John Doe\Downloads\FishVision" && call .venv...`.
- Windows immediately aborted with: `The system cannot find the path specified.`

### Root Cause 2: Missing Path Separator and Working Directory Confusion in Frontend Launch
In the frontend startup line:
```bat
start "FishVision React UI" /min cmd /c "cd /d "%PROJECT_ROOT%frontend" && npm run dev > ..\logs\frontend.log 2>&1"
```
Depending on whether `%PROJECT_ROOT%` had a trailing backslash or had been stripped via path expansion, `%PROJECT_ROOT%frontend` resolved to `FishVisionfrontend` (a non-existent directory), or suffered from the identical escaped quote defect (`\"`). Furthermore, redirecting output to `..\logs\frontend.log` relied on relative directory traversal from a directory that was never successfully entered.

### Root Cause 3: Non-Portable Virtual Environment Paths (`pyvenv.cfg` and `activate.bat`)
Python virtual environments (`.venv`) created on Windows contain absolute, machine-specific paths:
1. `.venv\pyvenv.cfg` contains:
   ```ini
   home = C:\Users\adars\AppData\Local\Programs\Python\Python312
   executable = C:\Users\adars\AppData\Local\Programs\Python\Python312\python.exe
   command = C:\Users\adars\AppData\Local\Programs\Python\Python312\python.exe -m venv ...
   ```
2. `.venv\Scripts\activate.bat` contains:
   ```bat
   set "VIRTUAL_ENV=C:\Users\adars\Downloads\FishVision_V2_App_Windows\FishVision_V2_App\.venv"
   ```
When `.venv` was extracted onto another machine where `C:\Users\adars` did not exist:
- Invoking `call .venv\Scripts\activate.bat` or `.venv\Scripts\python.exe` failed because the Windows stub loader could not locate the parent Python interpreter at `home`.
- The operating system reported: `The system cannot find the path specified.`
- Crucially, `run.bat` previously only checked `if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe"`. Because the `.exe` file stub was physically present in the extracted folder, `run.bat` assumed the environment was valid and skipped `FIRST_TIME_SETUP.bat`.

### Root Cause 4: Developer-Specific Fallback Paths in Audit Scripts
A secondary hardcoded path issue existed in `check_test_overlap.py` and `scripts_audit_phase2.py`, where default fallback paths in `os.environ.get()` referenced:
```text
C:\Users\adars\Downloads\classification_152_ready.zip\test
```
While not directly part of the runtime launcher, running test verification scripts on a teammate's laptop would fail due to this hardcoded path.

---

## 3. Exact Offending Files and Commands

| File | Line Number | Original Incorrect Command / Path | Defect Type |
| :--- | :--- | :--- | :--- |
| `run.bat` | 46 | `start "..." /min cmd /c "cd /d "%PROJECT_ROOT%" && call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app ..."` | Escaped quote `\"` syntax error; reliance on machine-specific `activate.bat` |
| `run.bat` | 54 | `start "..." /min cmd /c "cd /d "%PROJECT_ROOT%frontend" && npm run dev > ..\logs\frontend.log 2>&1"` | Escaped quote `\"` syntax error; path concatenation bug; invalid relative log redirection |
| `run.bat` | 17 | `if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" set "NEED_SETUP=1"` | False positive: file exists but is non-executable on a different machine |
| `check_test_overlap.py` | 7 | `r"C:\Users\adars\Downloads\classification_152_ready.zip\test"` | Machine-specific hardcoded username path |
| `scripts_audit_phase2.py` | 11–13 | `r"C:\Users\adars\Downloads\classification_152_ready.zip\..."` | Machine-specific hardcoded username path |

---

## 4. Corrected Path-Resolution Approach

### 4.1 Strict Path Normalization Without Trailing Backslashes
All batch files now use the standard, robust directory normalization idiom:
```bat
@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

for %%I in ("%~dp0.") do set "PROJECT_ROOT=%%~fI"
```
- `%~dp0` switches drive and directory.
- `for %%I in ("%~dp0.") do set "PROJECT_ROOT=%%~fI"` normalizes the path to an absolute path **without a trailing backslash**.
- All derived paths are cleanly declared with explicit backslashes:
  ```bat
  set "BACKEND_DIR=%PROJECT_ROOT%\backend"
  set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
  set "VENV_DIR=%PROJECT_ROOT%\.venv"
  set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
  set "CHECKPOINT_DIR=%PROJECT_ROOT%\checkpoints"
  set "DATA_DIR=%PROJECT_ROOT%\data"
  set "LOG_DIR=%PROJECT_ROOT%\logs"
  ```
  Because `PROJECT_ROOT` has no trailing backslash, quoting `"%BACKEND_DIR%"` never ends in `\"`.

### 4.2 Native Working Directory Management via `start /d`
Instead of chaining `cmd /c "cd /d ... && ..."` with fragile nested quotes, we utilize the native `/d` switch of the Windows `start` command:
- **Backend Launch:**
  ```bat
  start "FishVision Backend API" /d "%PROJECT_ROOT%" /min cmd /c ""%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > "%LOG_DIR%\backend.log" 2>&1"
  ```
- **Frontend Launch:**
  ```bat
  start "FishVision React UI" /d "%FRONTEND_DIR%" /min cmd /c "npm run dev -- --host 127.0.0.1 > "%LOG_DIR%\frontend.log" 2>&1"
  ```
- Notice that outer double quotes wrap the entire `cmd /c` argument string, allowing `cmd.exe` to strip the outer pair according to Microsoft specifications while preserving inner quotes around `"%PYTHON_EXE%"` and `"%LOG_DIR%\backend.log"`.
- Output is redirected directly to absolute paths `"%LOG_DIR%\backend.log"` and `"%LOG_DIR%\frontend.log"`.

### 4.3 Virtual Environment Portability & Validation
To prevent stale virtual environments from breaking on new laptops:
1. In `run.bat`:
   ```bat
   set "NEED_SETUP=0"
   if not exist "%PYTHON_EXE%" (
       set "NEED_SETUP=1"
   ) else (
       "%PYTHON_EXE%" -c "import sys" >nul 2>&1
       if errorlevel 1 (
           echo [SETUP REQUIRED] Python virtual environment is invalid for this machine.
           echo                 ^(Likely moved from another directory, drive, or user account^).
           set "NEED_SETUP=1"
       )
   )
   ```
2. In `FIRST_TIME_SETUP.bat`:
   ```bat
   if exist "%PYTHON_EXE%" (
       "%PYTHON_EXE%" -c "import sys" >nul 2>&1
       if errorlevel 1 (
           echo       Existing .venv is invalid or was created for a different machine.
           echo       Rebuilding fresh virtual environment...
           rmdir /s /q "%VENV_DIR%" >> "%SETUP_LOG%" 2>&1
       )
   )
   ```
If the virtual environment was created under another user's profile and cannot execute on the current machine, it is detected immediately, purged, and recreated cleanly using the local Python installation.

---

## 5. Files Modified

| File | Status | Nature of Change |
| :--- | :--- | :--- |
| `run.bat` | **Modified** | Dynamic root detection, pre-flight structure & checkpoint validation, venv execution test, `start /d` process invocation, readiness check, safe abort. |
| `stop.bat` | **Modified** | Dynamic root detection, targeted netstat PID extraction for ports 8000 and 5173, clean process termination. |
| `FIRST_TIME_SETUP.bat` | **Modified** | Dynamic root detection, broken-venv detection & recreation, Python & Node.js winget provisioning, automated setup log. |
| `tools/check_readiness.py` | **Modified** | Dynamic health waiter; validates specific FishVision API response payload (`status: ok` and `models: 5`). |
| `check_test_overlap.py` | **Modified** | Removed hardcoded `C:\Users\adars` string; replaced with dynamic relative path `ROOT.parent / ...`. |
| `scripts_audit_phase2.py` | **Modified** | Removed 3 hardcoded `C:\Users\adars` strings; replaced with dynamic relative paths. |

---

## 6. Remaining Risks or Limitations

1. **Port Collisions with Other Services:**  
   If another application (such as WSL relay, a third-party Docker container, or another Node/Python server) is already listening on ports 8000 or 5173, `stop.bat` will attempt to terminate the process listening on those ports. If that process is protected by administrative permissions, manual shutdown of the conflicting application is required.
2. **Execution Policy & Defender SmartScreen:**  
   When `.bat` files are extracted from a ZIP downloaded from the internet, Windows SmartScreen may present an untrusted file warning. Users must click "More Info" -> "Run Anyway".
3. **Absence of `winget` on Outdated Windows 10 Builds:**  
   If a teammate is running an obsolete Windows 10 build prior to 19041 without Windows App Installer (`winget`), automatic runtime installation is unavailable. The script clearly informs the user and prints direct manual download links for Python 3.12 and Node.js LTS.

