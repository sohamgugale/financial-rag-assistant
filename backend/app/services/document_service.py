import os
import hashlib
from typing import List, Dict, Tuple
from datetime import datetime
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_anthropic import AnthropicEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from app.core.config import settings
import json

class DocumentProcessor:
    """Process and manage documents for RAG system"""
    
    def __init__(self):
        self.embeddings = AnthropicEmbeddings(anthropic_api_key=settings.ANTHROPIC_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        self.vector_store = None
        self.documents_metadata: Dict = {}
        self._load_or_create_vector_store()
        
    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Load metadata if exists
        metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.documents_metadata = json.load(f)
        
        # Load vector store if exists
        index_path = os.path.join(settings.VECTOR_DB_PATH, "index.faiss")
        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(
                    settings.VECTOR_DB_PATH, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded existing vector store with {len(self.documents_metadata)} documents")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vector_store = None
    
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
    
    def create_chunks_with_metadata(
        self, 
        text: str, 
        document_id: str, 
        filename: str
    ) -> List[Document]:
        """Create chunks with rich metadata for citations"""
        chunks = []
        pages = text.split("[Page ")
        
        for page_section in pages[1:]:
            page_num_end = page_section.find("]")
            page_num = int(page_section[:page_num_end])
            page_text = page_section[page_num_end + 1:].strip()
            
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
        """Process uploaded document and add to vector store"""
        try:
            document_id = self._generate_document_id(filename)
            text, page_count = self.extract_text_from_pdf(file_path)
            chunks = self.create_chunks_with_metadata(text, document_id, filename)
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            else:
                self.vector_store.add_documents(chunks)
            
            self.vector_store.save_local(settings.VECTOR_DB_PATH)
            
            file_stats = os.stat(file_path)
            self.documents_metadata[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "pages": page_count,
                "chunks": len(chunks),
                "uploaded_at": datetime.now().isoformat(),
                "file_size": file_stats.st_size
            }
            
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
        """Delete document from vector store"""
        if document_id in self.documents_metadata:
            del self.documents_metadata[document_id]
            metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.documents_metadata, f, indent=2)
            return True
        return False

document_processor = DocumentProcessor()
