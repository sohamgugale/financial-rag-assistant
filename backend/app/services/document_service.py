import os
import hashlib
from typing import List, Dict, Tuple
from datetime import datetime
import pypdf
from rank_bm25 import BM25Okapi
from app.core.config import settings
import json

class Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

class BM25Retriever:
    def __init__(self, documents):
        self.documents = documents
        self.k = 5
        corpus = [doc.page_content.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(corpus)
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k]
        return [self.documents[i] for i in top_indices]

class DocumentProcessor:
    def __init__(self):
        self.all_documents = []
        self.retriever = None
        self.documents_metadata = {}
        self._load_metadata()
        
    def _load_metadata(self):
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
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:12]
    
    async def process_document(self, file_path: str, filename: str) -> Dict:
        try:
            document_id = self._generate_document_id(filename)
            
            # Extract PDF text
            text_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        # Create chunks (simple split by sentences)
                        sentences = text.split('. ')
                        for i in range(0, len(sentences), 5):
                            chunk = '. '.join(sentences[i:i+5])
                            if chunk.strip():
                                doc = Document(
                                    page_content=chunk,
                                    metadata={
                                        "document_id": document_id,
                                        "filename": filename,
                                        "page": page_num
                                    }
                                )
                                self.all_documents.append(doc)
            
            # Create retriever
            if self.all_documents:
                self.retriever = BM25Retriever(self.all_documents)
            
            # Save metadata
            file_stats = os.stat(file_path)
            self.documents_metadata[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "pages": page_count,
                "chunks": len([d for d in self.all_documents if d.metadata["document_id"] == document_id]),
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
        return list(self.documents_metadata.values())
    
    def get_document(self, document_id: str) -> Dict:
        return self.documents_metadata.get(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        if document_id in self.documents_metadata:
            self.all_documents = [d for d in self.all_documents if d.metadata.get("document_id") != document_id]
            if self.all_documents:
                self.retriever = BM25Retriever(self.all_documents)
            else:
                self.retriever = None
            del self.documents_metadata[document_id]
            metadata_path = os.path.join(settings.VECTOR_DB_PATH, "metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.documents_metadata, f, indent=2)
            return True
        return False

document_processor = DocumentProcessor()
