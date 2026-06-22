@echo off
chcp 65001 >nul
title SIM-NET Network Management System
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   SIM-NET - Smart Integrated Network Management System    ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Install requirements if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📦 Installing requirements...
pip install -q -r requirements.txt

echo.
echo 🗄️  Initializing database...
python database\db_manager.py

echo.
echo 🚀 Starting SIM-NET...
echo.
echo ============================================
echo Backend will run on: http://localhost:5000
echo Frontend will run on: http://localhost:8080
echo ============================================
echo.

:: Start Backend in new window
start "SIM-NET Backend" cmd /k "call venv\Scripts\activate.bat && python backend\app.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend in new window
start "SIM-NET Frontend" cmd /k "cd frontend && python -m http.server 8080"

:: Wait for frontend
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:8080

echo.
echo ✅ SIM-NET is starting...
echo 🌐 Opening browser...
echo.
echo Press any key to stop all servers...
pause >nul

:: Kill Python processes
taskkill /F /IM python.exe >nul 2>&1

echo.
echo 🛑 Servers stopped
echo 👋 Goodbye!
timeout /t 2 >nul
