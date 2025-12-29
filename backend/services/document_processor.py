"""
Document Processing Service
Handles extraction, cleaning, and intelligent chunking of financial documents
"""

import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from docx import Document
from loguru import logger


class DocumentProcessor:
    """
    Process various document formats and create intelligent chunks
    Specialized for financial documents (earnings reports, 10-Ks, research papers)
    """
    
    def __init__(self):
        self.financial_keywords = [
            'revenue', 'earnings', 'profit', 'loss', 'ebitda', 'cash flow',
            'balance sheet', 'income statement', 'assets', 'liabilities',
            'equity', 'valuation', 'market cap', 'pe ratio', 'guidance'
        ]
    
    def extract_text(self, filepath: str) -> str:
        """
        Extract text from PDF, DOCX, or TXT files
        
        Args:
            filepath: Path to the document
            
        Returns:
            Extracted text as string
        """
        try:
            if filepath.endswith('.pdf'):
                return self._extract_from_pdf(filepath)
            elif filepath.endswith('.docx'):
                return self._extract_from_docx(filepath)
            elif filepath.endswith('.txt'):
                return self._extract_from_txt(filepath)
            else:
                raise ValueError(f"Unsupported file format: {filepath}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {filepath}: {e}")
            raise
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(filepath)
            text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            raise
    
    def _extract_from_txt(self, filepath: str) -> str:
        """Extract text from TXT"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"TXT extraction error: {e}")
            raise
    
    def create_chunks(
        self,
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 200,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Create intelligent chunks from text with metadata
        Uses semantic boundaries for better context preservation
        
        Args:
            text: Input text to chunk
            chunk_size: Target size for each chunk
            chunk_overlap: Overlap between chunks
            metadata: Additional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean the text
        text = self._clean_text(text)
        
        # Split into paragraphs first
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            # If paragraph alone is larger than chunk_size, split it
            if paragraph_size > chunk_size:
                # Add current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk_dict(current_chunk, metadata, len(chunks)))
                    current_chunk = ""
                    current_size = 0
                
                # Split large paragraph into sentences
                sentences = self._split_into_sentences(paragraph)
                temp_chunk = ""
                
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) <= chunk_size:
                        temp_chunk += sentence + " "
                    else:
                        if temp_chunk:
                            chunks.append(self._create_chunk_dict(temp_chunk.strip(), metadata, len(chunks)))
                        temp_chunk = sentence + " "
                
                if temp_chunk:
                    current_chunk = temp_chunk
                    current_size = len(temp_chunk)
                    
            # If adding this paragraph exceeds chunk_size
            elif current_size + paragraph_size > chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append(self._create_chunk_dict(current_chunk, metadata, len(chunks)))
                
                # Start new chunk with overlap
                if chunk_overlap > 0 and chunks:
                    # Take last chunk_overlap characters from previous chunk
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    
                current_size = len(current_chunk)
                
            else:
                # Add paragraph to current chunk
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                current_size += paragraph_size
        
        # Add the last chunk
        if current_chunk:
            chunks.append(self._create_chunk_dict(current_chunk, metadata, len(chunks)))
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _create_chunk_dict(self, text: str, metadata: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
        """Create a chunk dictionary with text and metadata"""
        chunk = {
            'text': text.strip(),
            'chunk_index': chunk_index,
            'char_count': len(text),
            'has_financial_keywords': self._contains_financial_keywords(text)
        }
        
        # Add provided metadata
        if metadata:
            chunk.update(metadata)
        
        return chunk
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\$\%]', '', text)
        
        # Remove page numbers and headers/footers (common in PDFs)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split on double newlines or multiple spaces
        paragraphs = re.split(r'\n\n+|\r\n\r\n+', text)
        
        # Filter out empty paragraphs and very short ones
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50]
        
        return paragraphs
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (could be enhanced with NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _contains_financial_keywords(self, text: str) -> bool:
        """Check if text contains financial keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.financial_keywords)
