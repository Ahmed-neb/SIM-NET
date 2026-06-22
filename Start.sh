#!/bin/bash

# SIM-NET Startup Script for Linux/Mac
# ====================================

clear

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   SIM-NET - Smart Integrated Network Management System    ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo -e "${GREEN}✅ Python found${NC}"
echo ""

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -q -r requirements.txt

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python database/db_manager.py

echo ""
echo "🚀 Starting SIM-NET..."
echo ""
echo "============================================"
echo "Backend will run on: http://localhost:5000"
echo "Frontend will run on: http://localhost:8080"
echo "============================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Servers stopped${NC}"
    echo "👋 Goodbye!"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Start Backend
echo "🔹 Starting Backend..."
python backend/app.py &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start Frontend
echo "🔹 Starting Frontend..."
cd frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

# Wait for frontend
sleep 2

# Open browser
echo "🌐 Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8080
elif command -v open &> /dev/null; then
    open http://localhost:8080
fi

echo ""
echo -e "${GREEN}✅ SIM-NET is running!${NC}"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
