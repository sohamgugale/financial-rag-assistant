#!/bin/bash

# Financial Research Assistant - Quick Start Script
# This script helps set up and run the application quickly

set -e  # Exit on error

echo "🧠 Financial Research Assistant - Quick Start"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✓ Python and Node.js found"
echo ""

# Function to setup backend
setup_backend() {
    echo "📦 Setting up Backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "  Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        echo "  ⚠️  No .env file found. Creating from .env.example..."
        cp .env.example .env
        echo "  ⚠️  Please edit backend/.env and add your OPENAI_API_KEY"
        read -p "  Press Enter to continue..."
    fi
    
    cd ..
    echo "✓ Backend setup complete"
    echo ""
}

# Function to setup frontend
setup_frontend() {
    echo "📦 Setting up Frontend..."
    cd frontend
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo "  Installing dependencies..."
        npm install
    else
        echo "  Dependencies already installed"
    fi
    
    cd ..
    echo "✓ Frontend setup complete"
    echo ""
}

# Function to run the application
run_application() {
    echo "🚀 Starting Application..."
    echo ""
    echo "Starting backend server..."
    echo "(Backend will run on http://localhost:8000)"
    echo ""
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 3
    
    echo "Starting frontend server..."
    echo "(Frontend will run on http://localhost:3000)"
    echo ""
    
    # Start frontend
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✓ Application started successfully!"
    echo ""
    echo "📝 Access points:"
    echo "   Frontend:  http://localhost:3000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   API:       http://localhost:8000/api/v1"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    echo ""
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
}

# Main menu
echo "Select an option:"
echo "1) Setup only (install dependencies)"
echo "2) Run application (setup + start servers)"
echo "3) Exit"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        setup_backend
        setup_frontend
        echo "✨ Setup complete! Run './start.sh' and choose option 2 to start the application."
        ;;
    2)
        setup_backend
        setup_frontend
        run_application
        ;;
    3)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
