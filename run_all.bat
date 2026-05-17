@echo off
echo ===================================================
echo 🚀 STARTING COMPASS AI DEV ENVIRONMENT...
echo ===================================================

echo.
echo [1/2] Running Pytest Suite...
:: Using python -m bypasses the Windows PATH issues
python -m pytest tests/ -v

:: Check if tests passed (errorlevel 0 means success)
if %errorlevel% neq 0 (
    echo.
    echo ❌ TESTS FAILED! Stopping execution. Please fix the errors above.
    pause
    exit /b %errorlevel%
)

echo.
echo ✅ TESTS PASSED!
echo.
echo [2/2] Starting FastAPI Server with Uvicorn...
:: Using python -m uvicorn bypasses the command not found error
python -m uvicorn bob_core.main:app --reload

pause