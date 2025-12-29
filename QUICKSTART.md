# ⚡ Quick Start Guide

Get the Financial Research Assistant up and running in 5 minutes!

## 🎯 Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed  
3. **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Fast Setup (Automated)

### macOS/Linux:
```bash
./start.sh
# Select option 2 (Setup + Run)
```

### Windows:
```bash
start.bat
# Select option 2 (Setup + Run)
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Prompt for OpenAI API key
- Start both backend and frontend servers

## 🔧 Manual Setup (If Automated Fails)

### Backend (Terminal 1)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Start server
uvicorn app.main:app --reload
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access the App

- **Frontend UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Endpoint**: http://localhost:8000/api/v1

## 📝 First Steps

1. **Upload a PDF** - Drag and drop any PDF (try a 10-K or earnings report)
2. **Wait for processing** - Usually takes 10-30 seconds
3. **Ask questions** - Try: "What are the main revenue sources?"
4. **Explore features** - Check out Insights and Compare tabs

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Backend: Use port 8001 instead
uvicorn app.main:app --reload --port 8001

# Frontend: Use port 3001 instead  
npm run dev -- --port 3001
```

**Module not found?**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**OpenAI API error?**
```bash
# Check your .env file has the correct key
cat backend/.env  # Should show OPENAI_API_KEY=sk-...
```

## 📚 Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup instructions
- Check [README.md](README.md) for full documentation
- Review [PROJECT_HIGHLIGHTS.md](PROJECT_HIGHLIGHTS.md) for interview prep

## 🆘 Still Having Issues?

1. Check backend logs for error messages
2. Visit http://localhost:8000/docs to test API directly
3. Open browser DevTools (F12) to check frontend errors
4. Ensure you have credits in your OpenAI account

---

**Happy analyzing! 🎉**
