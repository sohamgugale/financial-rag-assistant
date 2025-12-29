# 🧠 Financial Research Assistant - AI RAG System

An advanced **Retrieval-Augmented Generation (RAG)** system specifically designed for financial document analysis. This project goes beyond basic PDF chat by offering multi-document comparison, automated insights extraction, citation tracking, and specialized financial analysis capabilities.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge)

## 🎯 Key Features

### Advanced RAG Capabilities
- **Intelligent Chunking**: Recursive character splitting with context preservation
- **Citation Tracking**: Page-level source attribution for all responses
- **Multi-Document Search**: Query across multiple financial documents simultaneously
- **Semantic Search**: FAISS vector database with OpenAI embeddings

### Financial-Specific Features
- **Document Comparison**: Compare up to 5 financial documents across multiple dimensions
- **Automated Insights**: Extract summaries, key points, financial metrics, and risk analysis
- **Confidence Scoring**: AI-generated confidence levels for each response
- **Document Metadata**: Track pages, chunks, and processing details

### Production-Ready Architecture
- **RESTful API**: Well-documented FastAPI backend with Pydantic validation
- **Modern Frontend**: React with Tailwind CSS for a polished user experience
- **Error Handling**: Comprehensive error handling and user feedback
- **Scalable Design**: Modular architecture ready for expansion

## 🏗️ Architecture

```
┌─────────────────┐
│   React UI      │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/JSON
┌────────▼────────┐
│   FastAPI       │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┐
    │          │              │
┌───▼──┐  ┌───▼────┐  ┌─────▼─────┐
│ FAISS│  │LangChain│  │ OpenAI    │
│Vector│  │  RAG   │  │Embeddings │
│  DB  │  │ Chain  │  │    API    │
└──────┘  └────────┘  └───────────┘
```

## 📋 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: RAG orchestration and document processing
- **OpenAI API**: GPT-3.5-turbo for generation + text-embedding-ada-002
- **FAISS**: Facebook AI Similarity Search for vector storage
- **PyPDF**: PDF text extraction
- **Pydantic**: Data validation and settings management

### Frontend
- **React 18**: Modern UI library with hooks
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **React Markdown**: Render AI responses
- **Lucide React**: Beautiful icon library

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/financial-rag-assistant.git
cd financial-rag-assistant
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Optional: Configure API URL
# Create .env.local and set VITE_API_URL if needed
```

4. **Run the Application**

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

5. **Access the Application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api/v1

## 📖 Usage Guide

### 1. Upload Documents
- Drag and drop PDF files (financial reports, 10-Ks, research papers)
- Maximum file size: 10MB
- Supported format: PDF only

### 2. Chat with Documents
- Ask natural language questions about your documents
- Filter by specific documents or search all
- View citations with page numbers
- Get confidence scores for each answer

**Example Questions:**
- "What were the key revenue drivers in Q3?"
- "Compare the operating margins across these reports"
- "What risks are mentioned in the 10-K?"
- "Summarize the cash flow situation"

### 3. Extract Insights
Select documents and choose insight type:
- **Summary**: Comprehensive overview
- **Key Points**: Bullet-point highlights
- **Financial Metrics**: Performance indicators
- **Risks**: Risk analysis and challenges

### 4. Compare Documents
- Select 2-5 documents
- Choose comparison dimension:
  - General comparison
  - Financial performance
  - Risk analysis
  - Growth opportunities

## 🔧 API Endpoints

### Documents
```
POST   /api/v1/upload          - Upload a PDF document
GET    /api/v1/documents       - List all documents
GET    /api/v1/documents/{id}  - Get document details
DELETE /api/v1/documents/{id}  - Delete a document
```

### Analysis
```
POST   /api/v1/query      - Query documents with Q&A
POST   /api/v1/insights   - Extract insights
POST   /api/v1/compare    - Compare documents
GET    /api/v1/health     - Health check
```

See [API Documentation](http://localhost:8000/docs) for detailed schemas and examples.

## 🐳 Docker Deployment

```bash
# Backend
cd backend
docker build -t financial-rag-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key financial-rag-backend

# Frontend
cd frontend
docker build -t financial-rag-frontend .
docker run -p 3000:3000 financial-rag-frontend
```

## 📊 Project Structure

```
financial-rag-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── core/
│   │   │   └── config.py          # Configuration
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── services/
│   │   │   ├── document_service.py # Document processing
│   │   │   └── rag_service.py      # RAG logic
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   ├── InsightsPanel.jsx
│   │   │   └── ComparisonPanel.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎨 Customization

### Modify LLM Settings
Edit `backend/app/core/config.py`:
```python
MODEL_NAME = "gpt-4"  # Use GPT-4 for better results
TEMPERATURE = 0.3     # Lower for more focused responses
CHUNK_SIZE = 1500     # Larger chunks for more context
```

### Change Vector Database
Replace FAISS with Pinecone or Chroma in `document_service.py`

### Add New Insight Types
Update `insight_types` in `rag_service.py` and frontend components

## 🧪 Testing

```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend development
cd frontend
npm run dev
```

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` files
- **File Upload**: Validates file types and sizes
- **Input Validation**: Pydantic schemas prevent injection
- **CORS**: Configured for development (restrict in production)

## 📈 Performance Optimization

- **Caching**: Implement Redis for vector search results
- **Async Processing**: Background tasks for large documents
- **Batch Processing**: Upload multiple documents simultaneously
- **CDN**: Serve frontend through CDN in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for RAG orchestration
- [OpenAI](https://openai.com/) for embeddings and language models
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

## 📧 Contact

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/financial-rag-assistant](https://github.com/yourusername/financial-rag-assistant)

---

**Built with ❤️ for smarter financial research**
