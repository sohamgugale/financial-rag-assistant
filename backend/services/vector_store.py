"""
Vector Store Manager
Handles FAISS vector database operations with hybrid search capabilities
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from sentence_transformers import SentenceTransformer
from loguru import logger
from datetime import datetime


class VectorStoreManager:
    """
    Manage FAISS vector store with semantic and keyword search
    Supports multiple retrieval strategies for optimal RAG performance
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector store with embedding model
        
        Args:
            model_name: SentenceTransformer model for embeddings
        """
        self.model_name = model_name
        self.embedding_model = None
        self.index = None
        self.documents = []  # List of document chunks with metadata
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self.index_path = "data/faiss_index.bin"
        self.documents_path = "data/documents.pkl"
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
    
    async def initialize(self):
        """Initialize embedding model and load existing index if available"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            self.dimension = self.embedding_model.get_sentence_embedding_dimension()
            
            # Try to load existing index
            if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
                self._load_index()
                logger.info(f"✅ Loaded existing index with {len(self.documents)} documents")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                logger.info("✅ Created new FAISS index")
                
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    async def add_documents(self, chunks: List[Dict[str, Any]], source_name: str):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            source_name: Name of source document
        """
        try:
            if not chunks:
                logger.warning("No chunks to add")
                return
            
            # Extract texts for embedding
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Add to FAISS index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents with enhanced metadata
            for i, chunk in enumerate(chunks):
                doc_entry = {
                    **chunk,
                    'source': source_name,
                    'embedding_index': len(self.documents),
                    'added_at': datetime.now().isoformat()
                }
                self.documents.append(doc_entry)
            
            # Save index
            self._save_index()
            
            logger.info(f"✅ Added {len(chunks)} chunks from {source_name}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of relevant documents with scores
        """
        try:
            if not self.documents:
                logger.warning("No documents in vector store")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            ).astype('float32')
            
            # Search in FAISS
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            # Prepare results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.documents):
                    # Convert L2 distance to similarity score (0-1 range)
                    similarity_score = 1 / (1 + dist)
                    
                    # Apply threshold if specified
                    if score_threshold and similarity_score < score_threshold:
                        continue
                    
                    doc = self.documents[idx].copy()
                    doc['similarity_score'] = float(similarity_score)
                    doc['distance'] = float(dist)
                    doc['retrieval_method'] = 'semantic'
                    results.append(doc)
            
            logger.info(f"Semantic search found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def keyword_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search (BM25-like scoring)
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        try:
            if not self.documents:
                return []
            
            # Extract query keywords
            query_keywords = set(query.lower().split())
            
            # Score each document
            scored_docs = []
            for doc in self.documents:
                text_lower = doc['text'].lower()
                
                # Calculate keyword match score
                matches = sum(1 for keyword in query_keywords if keyword in text_lower)
                
                if matches > 0:
                    # Simple TF-IDF-like scoring
                    score = matches / len(query_keywords)
                    
                    doc_copy = doc.copy()
                    doc_copy['keyword_score'] = score
                    doc_copy['retrieval_method'] = 'keyword'
                    scored_docs.append(doc_copy)
            
            # Sort by score and return top_k
            scored_docs.sort(key=lambda x: x['keyword_score'], reverse=True)
            results = scored_docs[:top_k]
            
            logger.info(f"Keyword search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic and keyword approaches
        
        Args:
            query: Search query
            top_k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            
        Returns:
            List of relevant documents with combined scores
        """
        try:
            # Perform both searches
            semantic_results = self.semantic_search(query, top_k=top_k * 2)
            keyword_results = self.keyword_search(query, top_k=top_k * 2)
            
            # Combine results
            doc_scores = {}
            
            # Add semantic scores
            for doc in semantic_results:
                doc_id = doc['embedding_index']
                doc_scores[doc_id] = {
                    'doc': doc,
                    'semantic_score': doc['similarity_score'] * semantic_weight,
                    'keyword_score': 0.0
                }
            
            # Add keyword scores
            for doc in keyword_results:
                doc_id = doc['embedding_index']
                if doc_id in doc_scores:
                    doc_scores[doc_id]['keyword_score'] = doc['keyword_score'] * keyword_weight
                else:
                    doc_scores[doc_id] = {
                        'doc': doc,
                        'semantic_score': 0.0,
                        'keyword_score': doc['keyword_score'] * keyword_weight
                    }
            
            # Calculate combined scores
            combined_results = []
            for doc_id, scores in doc_scores.items():
                combined_score = scores['semantic_score'] + scores['keyword_score']
                doc = scores['doc'].copy()
                doc['combined_score'] = combined_score
                doc['retrieval_method'] = 'hybrid'
                combined_results.append(doc)
            
            # Sort by combined score and return top_k
            combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
            results = combined_results[:top_k]
            
            logger.info(f"Hybrid search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        return len(self.documents)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents with metadata"""
        # Group by source
        sources = {}
        for doc in self.documents:
            source = doc.get('source', 'unknown')
            if source not in sources:
                sources[source] = {
                    'source': source,
                    'chunk_count': 0,
                    'added_at': doc.get('added_at', 'unknown')
                }
            sources[source]['chunk_count'] += 1
        
        return list(sources.values())
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from vector store
        Note: FAISS doesn't support deletion, so we rebuild the index
        """
        try:
            # Filter out documents from this source
            original_count = len(self.documents)
            self.documents = [doc for doc in self.documents if doc.get('source') != document_id]
            
            if len(self.documents) == original_count:
                return False  # Document not found
            
            # Rebuild index
            if self.documents:
                texts = [doc['text'] for doc in self.documents]
                embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
                
                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.index.add(embeddings.astype('float32'))
                
                # Update embedding indices
                for i, doc in enumerate(self.documents):
                    doc['embedding_index'] = i
            else:
                # Create empty index
                self.index = faiss.IndexFlatL2(self.dimension)
            
            # Save updated index
            self._save_index()
            
            logger.info(f"✅ Deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def _save_index(self):
        """Save FAISS index and documents to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
            logger.debug("Index saved successfully")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _load_index(self):
        """Load FAISS index and documents from disk"""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            logger.debug("Index loaded successfully")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise
