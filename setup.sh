#!/bin/bash

# Financial RAG Assistant - Quick Setup Script
# This script sets up both backend and frontend for development

set -e  # Exit on error

echo "🚀 Financial RAG Assistant - Quick Setup"
echo "========================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi
echo "✅ npm found: $(npm --version)"

echo ""

# Setup Backend
echo "🐍 Setting up Backend..."
echo "------------------------"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.template .env
    echo "⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
fi

# Create data directory
mkdir -p data

echo "✅ Backend setup complete!"
echo ""

cd ..

# Setup Frontend
echo "⚛️  Setting up Frontend..."
echo "------------------------"

cd frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo ""

cd ..

# Final instructions
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your OpenAI API key:"
echo "   Edit: backend/.env"
echo "   Add: OPENAI_API_KEY=your_key_here"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "📚 For more information, see README.md"
echo ""
