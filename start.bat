@echo off
REM Financial Research Assistant - Quick Start Script (Windows)

echo 🧠 Financial Research Assistant - Quick Start
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)

echo ✓ Python and Node.js found
echo.

:MENU
echo Select an option:
echo 1) Setup only (install dependencies)
echo 2) Run application (setup + start servers)
echo 3) Exit
echo.
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" goto SETUP_ONLY
if "%choice%"=="2" goto SETUP_AND_RUN
if "%choice%"=="3" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:SETUP_ONLY
call :SETUP_BACKEND
call :SETUP_FRONTEND
echo.
echo ✨ Setup complete! Run 'start.bat' and choose option 2 to start the application.
pause
exit /b 0

:SETUP_AND_RUN
call :SETUP_BACKEND
call :SETUP_FRONTEND
call :RUN_APPLICATION
exit /b 0

:SETUP_BACKEND
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo   Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo   Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo   ⚠️  No .env file found. Creating from .env.example...
    copy .env.example .env
    echo   ⚠️  Please edit backend\.env and add your OPENAI_API_KEY
    pause
)

cd ..
echo ✓ Backend setup complete
echo.
exit /b 0

:SETUP_FRONTEND
echo 📦 Setting up Frontend...
cd frontend

REM Install dependencies
if not exist "node_modules\" (
    echo   Installing dependencies...
    call npm install
) else (
    echo   Dependencies already installed
)

cd ..
echo ✓ Frontend setup complete
echo.
exit /b 0

:RUN_APPLICATION
echo 🚀 Starting Application...
echo.
echo Starting backend server...
echo (Backend will run on http://localhost:8000)
echo.

REM Start backend in new window
start "RAG Backend" cmd /k "cd backend && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo Starting frontend server...
echo (Frontend will run on http://localhost:3000)
echo.

REM Start frontend in new window
start "RAG Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✓ Application started successfully!
echo.
echo 📝 Access points:
echo    Frontend:  http://localhost:3000
echo    API Docs:  http://localhost:8000/docs
echo    API:       http://localhost:8000/api/v1
echo.
echo Close the command windows to stop the servers
echo.
pause
exit /b 0

:EXIT
echo Goodbye!
exit /b 0
