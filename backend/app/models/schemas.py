from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    pages: int
    chunks: int
    status: str
    uploaded_at: str

class QueryRequest(BaseModel):
    """Request model for chat queries"""
    query: str = Field(..., min_length=1, max_length=1000)
    document_ids: Optional[List[str]] = None
    include_citations: bool = True
    max_results: int = Field(default=5, ge=1, le=10)

class Citation(BaseModel):
    """Citation information for source tracking"""
    document_id: str
    document_name: str
    page_number: int
    chunk_text: str
    similarity_score: float

class QueryResponse(BaseModel):
    """Response model for chat queries"""
    answer: str
    citations: List[Citation]
    confidence: float
    processing_time: float

class DocumentInfo(BaseModel):
    """Document metadata"""
    document_id: str
    filename: str
    pages: int
    chunks: int
    uploaded_at: str
    file_size: int

class DocumentListResponse(BaseModel):
    """Response model for listing documents"""
    documents: List[DocumentInfo]
    total_count: int

class InsightRequest(BaseModel):
    """Request model for extracting insights"""
    document_ids: List[str]
    insight_type: str = Field(default="summary", pattern="^(summary|key_points|financial_metrics|risks)$")

class InsightResponse(BaseModel):
    """Response model for insights"""
    insight_type: str
    content: str
    documents_analyzed: List[str]
    generated_at: str

class ComparisonRequest(BaseModel):
    """Request model for document comparison"""
    document_ids: List[str] = Field(..., min_items=2, max_items=5)
    comparison_type: str = Field(default="general", pattern="^(general|financial|risks|opportunities)$")

class ComparisonResponse(BaseModel):
    """Response model for document comparison"""
    comparison: str
    documents: List[str]
    key_differences: List[str]
    similarities: List[str]
    generated_at: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    documents_loaded: int
