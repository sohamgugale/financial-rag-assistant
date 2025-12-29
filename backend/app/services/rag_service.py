import time
from typing import List, Dict, Tuple
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.services.document_service import document_processor
from app.models.schemas import Citation

class RAGService:
    """Retrieval Augmented Generation service for financial documents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
    def _create_qa_prompt(self) -> PromptTemplate:
        """Create prompt template for QA"""
        template = """You are a financial research assistant helping analyze financial documents. 
        Use the following context to answer the question. If you're not sure, say so clearly.
        Always cite which document and page your information comes from.
        
        Context: {context}
        
        Question: {question}
        
        Provide a detailed answer with specific references to the documents:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _filter_documents_by_id(self, document_ids: List[str]) -> List:
        """Filter vector store results by document IDs"""
        # This is a simplified version - in production, you'd want more sophisticated filtering
        return None
    
    async def query_documents(
        self,
        query: str,
        document_ids: List[str] = None,
        max_results: int = 5
    ) -> Tuple[str, List[Citation], float]:
        """Query documents and return answer with citations"""
        start_time = time.time()
        
        if document_processor.vector_store is None:
            return "No documents available. Please upload documents first.", [], 0.0
        
        try:
            # Retrieve relevant chunks
            retriever = document_processor.vector_store.as_retriever(
                search_kwargs={"k": max_results}
            )
            
            # Create QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self._create_qa_prompt()}
            )
            
            # Get answer
            result = qa_chain({"query": query})
            answer = result["result"]
            source_docs = result["source_documents"]
            
            # Create citations
            citations = []
            for doc in source_docs:
                citation = Citation(
                    document_id=doc.metadata.get("document_id", "unknown"),
                    document_name=doc.metadata.get("filename", "unknown"),
                    page_number=doc.metadata.get("page", 0),
                    chunk_text=doc.page_content[:200] + "...",
                    similarity_score=0.85  # FAISS doesn't return scores by default
                )
                citations.append(citation)
            
            # Filter citations by document_ids if provided
            if document_ids:
                citations = [c for c in citations if c.document_id in document_ids]
            
            processing_time = time.time() - start_time
            confidence = min(0.9, len(citations) * 0.15)  # Simple confidence metric
            
            return answer, citations, confidence, processing_time
            
        except Exception as e:
            return f"Error processing query: {str(e)}", [], 0.0, 0.0
    
    async def extract_insights(
        self,
        document_ids: List[str],
        insight_type: str
    ) -> str:
        """Extract insights from specified documents"""
        
        if document_processor.vector_store is None:
            return "No documents available."
        
        # Get document names
        doc_names = [
            document_processor.get_document(doc_id)["filename"] 
            for doc_id in document_ids 
            if document_processor.get_document(doc_id)
        ]
        
        # Create insight-specific prompts
        prompts = {
            "summary": f"Provide a comprehensive summary of the key information from these financial documents: {', '.join(doc_names)}",
            "key_points": f"Extract and list the most important key points from these documents: {', '.join(doc_names)}",
            "financial_metrics": f"Identify and summarize the key financial metrics and performance indicators from these documents: {', '.join(doc_names)}",
            "risks": f"Analyze and summarize the main risks and challenges mentioned in these documents: {', '.join(doc_names)}"
        }
        
        query = prompts.get(insight_type, prompts["summary"])
        
        # Use the query function
        answer, _, _, _ = await self.query_documents(query, document_ids, max_results=10)
        
        return answer
    
    async def compare_documents(
        self,
        document_ids: List[str],
        comparison_type: str
    ) -> Tuple[str, List[str], List[str]]:
        """Compare multiple documents"""
        
        if len(document_ids) < 2:
            return "Need at least 2 documents for comparison", [], []
        
        # Get document names
        doc_names = [
            document_processor.get_document(doc_id)["filename"] 
            for doc_id in document_ids 
            if document_processor.get_document(doc_id)
        ]
        
        # Create comparison prompts
        prompts = {
            "general": f"Compare and contrast these documents: {', '.join(doc_names)}. Highlight key differences and similarities.",
            "financial": f"Compare the financial performance and metrics across these documents: {', '.join(doc_names)}",
            "risks": f"Compare the risk profiles and challenges mentioned in these documents: {', '.join(doc_names)}",
            "opportunities": f"Compare the opportunities and growth prospects mentioned in these documents: {', '.join(doc_names)}"
        }
        
        query = prompts.get(comparison_type, prompts["general"])
        
        # Use the query function with higher max_results for comparison
        answer, citations, _, _ = await self.query_documents(query, document_ids, max_results=15)
        
        # Extract differences and similarities (simplified)
        differences = [
            "Document-specific metrics vary",
            "Different reporting periods",
            "Varied focus areas"
        ]
        
        similarities = [
            "Common industry trends",
            "Similar reporting standards",
            "Comparable structure"
        ]
        
        return answer, differences, similarities

# Global instance
rag_service = RAGService()
