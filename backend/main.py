"""
Financial RAG Assistant - Advanced Retrieval-Augmented Generation System
Specialized for financial documents with hybrid search, re-ranking, and citation tracking
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import json
from loguru import logger
import uvicorn

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStoreManager
from services.rag_engine import RAGEngine
from services.cache_manager import CacheManager

# Initialize FastAPI app
app = FastAPI(
    title="Financial RAG Assistant",
    description="Advanced RAG system for financial document analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
doc_processor = DocumentProcessor()
vector_store = VectorStoreManager()
rag_engine = RAGEngine(vector_store)
cache_manager = CacheManager()

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User's question")
    conversation_id: Optional[str] = None
    use_hybrid_search: bool = True
    top_k: int = 5
    temperature: float = 0.7

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    tokens_used: int
    processing_time: float
    search_strategy: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    vector_store_documents: int
    cache_size: int
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Financial RAG Assistant")
    
    # Load environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  OPENAI_API_KEY not set - set it in .env file")
    
    # Initialize vector store
    await vector_store.initialize()
    logger.info("✅ Vector store initialized")
    
    # Load sample documents if available
    sample_dir = "../sample_documents"
    if os.path.exists(sample_dir) and os.listdir(sample_dir):
        logger.info(f"📚 Loading sample documents from {sample_dir}")
        for filename in os.listdir(sample_dir):
            if filename.endswith(('.pdf', '.docx', '.txt')):
                filepath = os.path.join(sample_dir, filename)
                try:
                    await process_document_file(filepath, filename)
                    logger.info(f"✅ Loaded: {filename}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {filename}: {e}")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_store_documents=vector_store.get_document_count(),
        cache_size=cache_manager.get_cache_size(),
        timestamp=datetime.now().isoformat()
    )


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a financial document (PDF, DOCX, TXT)
    Creates vector embeddings and stores in FAISS
    """
    try:
        # Validate file type
        allowed_types = ['.pdf', '.docx', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document
        chunks_created = await process_document_file(temp_path, file.filename)
        
        # Clean up
        os.remove(temp_path)
        
        # Generate document ID
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            chunks_created=chunks_created,
            status="success",
            message=f"Successfully processed {file.filename} into {chunks_created} chunks"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with advanced retrieval and generation
    Supports hybrid search, conversation memory, and citation tracking
    """
    try:
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"{request.query}_{request.use_hybrid_search}_{request.top_k}"
        cached_response = cache_manager.get(cache_key)
        
        if cached_response:
            logger.info(f"📦 Cache hit for query: {request.query[:50]}...")
            cached_response['processing_time'] = (datetime.now() - start_time).total_seconds()
            return QueryResponse(**cached_response)
        
        # Generate response using RAG engine
        result = await rag_engine.generate_response(
            query=request.query,
            conversation_id=request.conversation_id,
            use_hybrid_search=request.use_hybrid_search,
            top_k=request.top_k,
            temperature=request.temperature
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        result['processing_time'] = processing_time
        
        # Cache the response
        cache_manager.set(cache_key, result, ttl=3600)  # Cache for 1 hour
        
        logger.info(f"✅ Query processed in {processing_time:.2f}s")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all documents in the vector store"""
    try:
        documents = vector_store.list_documents()
        return {
            "total_documents": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the vector store"""
    try:
        success = await vector_store.delete_document(document_id)
        if success:
            return {"status": "success", "message": f"Deleted document {document_id}"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Retrieve conversation history"""
    try:
        history = rag_engine.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "message_count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        rag_engine.clear_conversation(conversation_id)
        return {"status": "success", "message": f"Cleared conversation {conversation_id}"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_file(filepath: str, filename: str) -> int:
    """Helper function to process a document file"""
    # Extract text from document
    text = doc_processor.extract_text(filepath)
    
    # Create chunks with metadata
    chunks = doc_processor.create_chunks(
        text=text,
        chunk_size=800,
        chunk_overlap=200,
        metadata={
            'filename': filename,
            'upload_date': datetime.now().isoformat(),
            'document_type': 'financial_document'
        }
    )
    
    # Add to vector store
    await vector_store.add_documents(chunks, filename)
    
    return len(chunks)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
