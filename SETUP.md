# 📚 Setup Guide - Financial Research Assistant

This guide will walk you through setting up the Financial Research Assistant RAG system on your local machine.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Troubleshooting](#troubleshooting)
6. [Docker Setup (Alternative)](#docker-setup)

## Prerequisites

### Required Software
- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher**: [Download Node.js](https://nodejs.org/)
- **Git**: [Download Git](https://git-scm.com/)

### Required API Keys
- **OpenAI API Key**: [Get your key here](https://platform.openai.com/api-keys)
  - You'll need credits in your OpenAI account
  - This project uses `gpt-3.5-turbo` and `text-embedding-ada-002`

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **OS**: Windows, macOS, or Linux

## Backend Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/financial-rag-assistant.git
cd financial-rag-assistant
```

### Step 2: Set Up Python Environment

**For macOS/Linux:**
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

**For Windows:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies
```bash
# Make sure your virtual environment is activated
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- LangChain (RAG framework)
- OpenAI Python SDK
- FAISS (vector database)
- PyPDF (PDF processing)
- And other dependencies

**Expected time**: 2-5 minutes depending on internet speed

### Step 4: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your text editor
# On macOS: open .env
# On Windows: notepad .env
# On Linux: nano .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DEBUG=False
```

⚠️ **Important**: Never commit your `.env` file to version control!

### Step 5: Verify Backend Installation
```bash
# Make sure you're in the backend directory with venv activated
python -c "import fastapi, langchain, openai; print('All imports successful!')"
```

If you see "All imports successful!", you're ready to go!

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
# From the project root
cd frontend
```

### Step 2: Install Node Dependencies
```bash
npm install
```

This will install:
- React and React DOM
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- Other dependencies

**Expected time**: 1-3 minutes

### Step 3: Configure API URL (Optional)
If your backend is running on a different port or host, create `.env.local`:

```bash
# Create .env.local
touch .env.local  # On Windows: type nul > .env.local
```

Add the following:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Note**: This is optional. The default is `http://localhost:8000/api/v1`

### Step 4: Verify Frontend Installation
```bash
npm run build
```

If the build completes without errors, you're ready!

## Running the Application

You'll need **two terminal windows** - one for backend, one for frontend.

### Terminal 1: Start Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify**: Visit http://localhost:8000/docs to see the API documentation

### Terminal 2: Start Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

You should see:
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Verify**: Visit http://localhost:3000 to see the application

## First Use

1. **Open your browser** to http://localhost:3000
2. **Upload a PDF** document (try a financial report or research paper)
3. **Wait for processing** (you'll see a success message)
4. **Ask a question** in the chat interface
5. **Explore insights** and comparison features

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Make sure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: `openai.error.AuthenticationError`
```bash
# Solution: Check your OpenAI API key in .env
cat .env  # Verify OPENAI_API_KEY is set correctly
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use a different port
uvicorn app.main:app --reload --port 8001

# Update frontend .env.local to match:
VITE_API_URL=http://localhost:8001/api/v1
```

**Problem**: `ImportError: cannot import name 'FAISS'`
```bash
# Solution: Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu==1.7.4
```

### Frontend Issues

**Problem**: `npm install` fails
```bash
# Solution: Clear npm cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Port 3000 already in use
```bash
# Solution: Kill the process or use a different port
# Find the process:
lsof -ti:3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Or specify a different port:
npm run dev -- --port 3001
```

**Problem**: "Failed to fetch" errors in browser
```bash
# Solution: 
# 1. Check backend is running (http://localhost:8000/health)
# 2. Check CORS settings in backend/app/main.py
# 3. Clear browser cache and hard reload (Ctrl+Shift+R)
```

### PDF Processing Issues

**Problem**: PDF upload fails
- **Check file size**: Maximum 10MB
- **Check format**: Only PDF supported
- **Check content**: Ensure PDF has extractable text (not just images)

**Problem**: No text extracted from PDF
```bash
# Some PDFs are image-based. Try:
# 1. Use a different PDF
# 2. OCR the PDF first
# 3. Check backend logs for errors
```

## Docker Setup

If you prefer using Docker:

### Step 1: Install Docker
- [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/vector_store:/app/vector_store

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
```

### Step 3: Run with Docker Compose
```bash
# Create .env in project root with your OpenAI key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start both services
docker-compose up --build

# Stop services
docker-compose down
```

## Next Steps

Once everything is running:

1. **Read the API documentation**: http://localhost:8000/docs
2. **Test with sample documents**: Try uploading a 10-K or earnings report
3. **Explore the features**: Chat, insights, and comparison
4. **Customize**: Modify settings in `backend/app/core/config.py`

## Getting Help

- **Check logs**: Backend terminal shows detailed error messages
- **API errors**: Visit http://localhost:8000/docs and test endpoints directly
- **Frontend errors**: Open browser DevTools (F12) and check Console
- **GitHub Issues**: [Report bugs or ask questions](https://github.com/yourusername/financial-rag-assistant/issues)

## Development Tips

### Auto-reload
Both servers support hot-reload:
- **Backend**: Edit Python files, server reloads automatically
- **Frontend**: Edit React components, page updates automatically

### Debugging Backend
```bash
# Add print statements or use debugger
import pdb; pdb.set_trace()  # Set breakpoint

# View detailed logs
uvicorn app.main:app --reload --log-level debug
```

### Debugging Frontend
```bash
# Use React DevTools browser extension
# Add console.log() in components
console.log('Documents:', documents);
```

---

**Setup Complete! 🎉**

You now have a fully functional Financial Research Assistant RAG system running locally!
