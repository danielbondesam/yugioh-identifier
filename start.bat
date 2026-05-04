@echo off
REM Yu-Gi-Oh Identifier - Start Script for Windows

echo.
echo 🎴 Yu-Gi-Oh Card Identifier
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16+
    exit /b 1
)

echo ✓ Python and Node.js found
echo.
echo ========================================
echo Setup Instructions
echo ========================================
echo.
echo 1. Open a NEW Command Prompt window
echo.
echo 2. In the new window, run:
echo    cd backend
echo    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. Wait for message: "Uvicorn running on http://0.0.0.0:8000"
echo.
echo 4. Open ANOTHER Command Prompt window
echo.
echo 5. In that window, run:
echo    cd frontend
echo    npm start
echo.
echo 6. Your browser should open at http://localhost:3000
echo.
echo ========================================
echo Backend API docs: http://localhost:8000/docs
echo ========================================
echo.
pause
