import os
import hashlib
from typing import List, Dict, Tuple
from datetime import datetime
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from app.core.config import settings
import json

class DocumentProcessor:
    """Process and manage documents for RAG system"""
    
    def __init__(self):
        # Use BM25 - lightweight keyword search, no embeddings needed!
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        self.retriever = None
        self.all_documents = []
        self.documents_metadata: Dict = {}
        self._load_metadata()
        
    def _load_metadata(self):
        """Load existing metadata"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    self.documents_metadata = json.load(f)
            except:
                self.documents_metadata = {}
    
    def _generate_document_id(self, filename: str) -> str:
        """Generate unique document ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{filename}{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int]:
        """Extract text from PDF and return text with page count"""
        text_content = []
        page_count = 0
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"[Page {page_num}]\n{text}")
        
        return "\n\n".join(text_content), page_count
    
    def create_chunks_with_metadata(self, text: str, document_id: str, filename: str) -> List[Document]:
        """Create chunks with rich metadata for citations"""
        chunks = []
        pages = text.split("[Page ")
        
        for page_section in pages[1:]:
            page_num_end = page_section.find("]")
            if page_num_end == -1:
                continue
            page_num = int(page_section[:page_num_end])
            page_text = page_section[page_num_end + 1:].strip()
            
            if not page_text:
                continue
            
            page_chunks = self.text_splitter.create_documents(
                texts=[page_text],
                metadatas=[{
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "chunk_index": 0
                }]
            )
            
            for idx, chunk in enumerate(page_chunks):
                chunk.metadata["chunk_index"] = idx
                chunks.append(chunk)
        
        return chunks
    
    async def process_document(self, file_path: str, filename: str) -> Dict:
        """Process uploaded document and add to retriever"""
        try:
            document_id = self._generate_document_id(filename)
            text, page_count = self.extract_text_from_pdf(file_path)
            chunks = self.create_chunks_with_metadata(text, document_id, filename)
            
            if not chunks:
                raise Exception("No text could be extracted from the PDF")
            
            # Add to document list
            self.all_documents.extend(chunks)
            
            # Recreate BM25 retriever with all documents
            self.retriever = BM25Retriever.from_documents(self.all_documents)
            self.retriever.k = settings.TOP_K
            
            file_stats = os.stat(file_path)
            self.documents_metadata[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "pages": page_count,
                "chunks": len(chunks),
                "uploaded_at": datetime.now().isoformat(),
                "file_size": file_stats.st_size
            }
            
            # Save metadata
            metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.documents_metadata, f, indent=2)
            
            return self.documents_metadata[document_id]
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def get_all_documents(self) -> List[Dict]:
        """Get all uploaded documents"""
        return list(self.documents_metadata.values())
    
    def get_document(self, document_id: str) -> Dict:
        """Get specific document metadata"""
        return self.documents_metadata.get(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        if document_id in self.documents_metadata:
            # Remove from documents list
            self.all_documents = [
                doc for doc in self.all_documents 
                if doc.metadata.get("document_id") != document_id
            ]
            
            # Recreate retriever
            if self.all_documents:
                self.retriever = BM25Retriever.from_documents(self.all_documents)
                self.retriever.k = settings.TOP_K
            else:
                self.retriever = None
            
            del self.documents_metadata[document_id]
            
            metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.documents_metadata, f, indent=2)
            
            return True
        return False

document_processor = DocumentProcessor()
