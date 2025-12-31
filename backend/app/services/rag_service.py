import time
from typing import List, Dict, Tuple
import anthropic
from app.core.config import settings
from app.services.document_service import document_processor
from app.models.schemas import Citation

class RAGService:
    """Simple RAG service using Anthropic"""
    
    def __init__(self):
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        
    async def query_documents(
        self,
        query: str,
        document_ids: List[str] = None,
        max_results: int = 5
    ) -> Tuple[str, List[Citation], float, float]:
        """Query documents and return answer"""
        start_time = time.time()
        
        if document_processor.retriever is None:
            return "No documents available. Please upload documents first.", [], 0.0, 0.0
        
        try:
            # Get documents
            document_processor.retriever.k = max_results
            docs = document_processor.retriever.get_relevant_documents(query)
            
            # Build context
            context = "\n\n".join([
                f"Document: {doc.metadata.get('filename')}\nPage: {doc.metadata.get('page')}\n{doc.page_content}"
                for doc in docs
            ])
            
            # Call Anthropic
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer based on the context above:"
                }]
            )
            
            answer = message.content[0].text
            
            # Build citations
            citations = []
            for doc in docs:
                citation = Citation(
                    document_id=doc.metadata.get("document_id", "unknown"),
                    document_name=doc.metadata.get("filename", "unknown"),
                    page_number=doc.metadata.get("page", 0),
                    chunk_text=doc.page_content[:200],
                    similarity_score=0.85
                )
                citations.append(citation)
            
            processing_time = time.time() - start_time
            confidence = min(0.9, len(citations) * 0.15)
            
            return answer, citations, confidence, processing_time
            
        except Exception as e:
            return f"Error: {str(e)}", [], 0.0, 0.0
    
    async def extract_insights(self, document_ids: List[str], insight_type: str) -> str:
        answer, _, _, _ = await self.query_documents(f"Provide {insight_type} from the documents", document_ids, 10)
        return answer
    
    async def compare_documents(self, document_ids: List[str], comparison_type: str) -> Tuple[str, List[str], List[str]]:
        answer, _, _, _ = await self.query_documents(f"Compare these documents: {comparison_type}", document_ids, 15)
        return answer, ["Different metrics"], ["Common structure"]

rag_service = RAGService()
