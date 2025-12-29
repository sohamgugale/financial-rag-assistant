import os
import shutil
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import (
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    DocumentListResponse,
    DocumentInfo,
    InsightRequest,
    InsightResponse,
    ComparisonRequest,
    ComparisonResponse,
    HealthResponse
)
from app.services.document_service import document_processor
from app.services.rag_service import rag_service
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        documents_loaded=len(document_processor.documents_metadata)
    )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Save uploaded file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        metadata = await document_processor.process_document(file_path, file.filename)
        
        return DocumentUploadResponse(
            document_id=metadata["document_id"],
            filename=metadata["filename"],
            pages=metadata["pages"],
            chunks=metadata["chunks"],
            status="processed",
            uploaded_at=metadata["uploaded_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents"""
    documents = document_processor.get_all_documents()
    
    doc_infos = [
        DocumentInfo(**doc) for doc in documents
    ]
    
    return DocumentListResponse(
        documents=doc_infos,
        total_count=len(doc_infos)
    )

@router.get("/documents/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str):
    """Get specific document information"""
    doc = document_processor.get_document(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentInfo(**doc)

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    success = document_processor.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"status": "deleted", "document_id": document_id}

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents with natural language"""
    
    answer, citations, confidence, processing_time = await rag_service.query_documents(
        query=request.query,
        document_ids=request.document_ids,
        max_results=request.max_results
    )
    
    # Filter citations if not requested
    if not request.include_citations:
        citations = []
    
    return QueryResponse(
        answer=answer,
        citations=citations,
        confidence=confidence,
        processing_time=processing_time
    )

@router.post("/insights", response_model=InsightResponse)
async def extract_insights(request: InsightRequest):
    """Extract insights from documents"""
    
    # Validate document IDs
    for doc_id in request.document_ids:
        if not document_processor.get_document(doc_id):
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    content = await rag_service.extract_insights(
        document_ids=request.document_ids,
        insight_type=request.insight_type
    )
    
    doc_names = [
        document_processor.get_document(doc_id)["filename"]
        for doc_id in request.document_ids
    ]
    
    return InsightResponse(
        insight_type=request.insight_type,
        content=content,
        documents_analyzed=doc_names,
        generated_at=datetime.now().isoformat()
    )

@router.post("/compare", response_model=ComparisonResponse)
async def compare_documents(request: ComparisonRequest):
    """Compare multiple documents"""
    
    # Validate document IDs
    for doc_id in request.document_ids:
        if not document_processor.get_document(doc_id):
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    comparison, differences, similarities = await rag_service.compare_documents(
        document_ids=request.document_ids,
        comparison_type=request.comparison_type
    )
    
    doc_names = [
        document_processor.get_document(doc_id)["filename"]
        for doc_id in request.document_ids
    ]
    
    return ComparisonResponse(
        comparison=comparison,
        documents=doc_names,
        key_differences=differences,
        similarities=similarities,
        generated_at=datetime.now().isoformat()
    )
