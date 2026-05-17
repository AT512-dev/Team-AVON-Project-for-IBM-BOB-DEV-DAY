@echo off
setlocal enabledelayedexpansion

echo.
echo ===================================================
echo    COMPASS AI - FULL TEST + DEV LAUNCHER
echo ===================================================
echo.

cd /d "%~dp0"
echo [ROOT] %CD%
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python not found. Install Python 3.12+ and add to PATH.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK]   %%v
echo.

if exist "venv\Scripts\activate.bat" (
    echo [OK]   Activating venv\
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK]   Activating .venv\
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] No venv found, using system Python.
)
echo.

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [WARN] .env missing - copied from .env.example. Fill in your API keys.
    ) else (
        echo [WARN] No .env found. WatsonX calls may fail.
    )
) else (
    echo [OK]   .env found.
)
echo.

echo [DEPS] Installing requirements...
if not exist "requirements.txt" (
    echo [WARN] requirements.txt not found, skipping.
    goto :run_tests
)

python -m pip install -r requirements.txt -q --disable-pip-version-check 1>pip_install.log 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] pip install failed. See pip_install.log for details.
    type pip_install.log
    del pip_install.log
    pause
    exit /b 1
)
del pip_install.log
echo [OK]   Dependencies ready.
echo.

:run_tests
echo ===================================================
echo    STEP 1 of 3  -  PYTEST
echo ===================================================
echo.

if not exist "tests\" (
    echo [WARN] No tests\ folder - skipping.
    goto :smoke
)

python -m pytest tests/ -v --tb=short
set PYTEST_EXIT=%errorlevel%
echo.

if %PYTEST_EXIT% neq 0 (
    echo [FAIL] Tests failed.
    echo.
    echo   1 = Stop here and fix tests
    echo   2 = Skip and launch servers anyway
    echo.
    choice /c 12 /n /m "Your choice: "
    if errorlevel 2 goto :smoke
    echo [EXIT] Fix the failing tests, then re-run this script.
    pause
    exit /b %PYTEST_EXIT%
)
echo [OK]   All tests passed.
echo.

:smoke
echo ===================================================
echo    STEP 2 of 3  -  ENDPOINT SMOKE TEST
echo ===================================================
echo.
echo [INFO] Spinning up a temporary backend on port 8001...
start /b "" python -m uvicorn bob_core.main:app --port 8001 --log-level error
timeout /t 4 /nobreak >nul

python smoke_helper.py
set SMOKE_EXIT=%errorlevel%

for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8001 "') do (
    taskkill /f /pid %%p >nul 2>&1
)

if %SMOKE_EXIT% neq 0 (
    echo.
    echo [FAIL] Smoke test failed. Fix the issues above, then re-run.
    pause
    exit /b %SMOKE_EXIT%
)
echo.

:launch
echo ===================================================
echo    STEP 3 of 3  -  LAUNCHING SERVERS
echo ===================================================
echo.

echo [INFO] Starting FastAPI backend on http://localhost:8000
start "Compass AI  -  Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn bob_core.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

if exist "navigator_ui\package.json" (
    echo [INFO] Starting Next.js frontend on http://localhost:3000
    start "Compass AI  -  Frontend" cmd /k "cd /d "%~dp0navigator_ui" && npm run dev"
) else (
    echo [WARN] navigator_ui\package.json not found. Start frontend manually.
)

echo.
echo ===================================================
echo    ALL SYSTEMS GO
echo ===================================================
echo.
echo   Backend   :  http://localhost:8000
echo   API Docs  :  http://localhost:8000/docs
echo   Frontend  :  http://localhost:3000
echo.
echo   Close the two terminal windows to stop the servers.
echo.
pause