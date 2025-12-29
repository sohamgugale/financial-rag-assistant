"""
RAG Engine - Advanced Retrieval-Augmented Generation
Implements query expansion, re-ranking, citation tracking, and conversation memory
"""

import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger
import json
from datetime import datetime


class RAGEngine:
    """
    Advanced RAG engine for financial document Q&A
    Features: query expansion, multi-step retrieval, re-ranking, citations
    """
    
    def __init__(self, vector_store):
        """
        Initialize RAG engine
        
        Args:
            vector_store: VectorStoreManager instance
        """
        self.vector_store = vector_store
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversations = {}  # Store conversation histories
        
        # Model configuration
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 2000
        
        # System prompts
        self.query_expansion_prompt = """You are an expert at expanding financial research queries.
Given a user's question, generate 2-3 related questions that would help retrieve more comprehensive information.
Focus on different aspects, perspectives, or related concepts.

User Question: {query}

Return only the expanded queries as a JSON array, like: ["query1", "query2", "query3"]"""

        self.rag_system_prompt = """You are a financial research assistant specialized in analyzing documents.

Guidelines:
1. Provide accurate, data-driven answers based ONLY on the provided context
2. When citing information, reference the specific document source
3. If the context doesn't contain enough information, clearly state this
4. Use financial terminology appropriately
5. Highlight key metrics, numbers, and trends
6. Be concise but comprehensive

Context Documents:
{context}

Previous Conversation:
{conversation_history}"""

        self.rerank_prompt = """Score how relevant this document chunk is to answering the user's question.
Consider: relevance, specificity, completeness of information.

Question: {query}

Document: {document}

Return only a relevance score from 0.0 to 1.0"""
    
    async def generate_response(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        use_hybrid_search: bool = True,
        top_k: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate response using RAG pipeline
        
        Args:
            query: User's question
            conversation_id: ID for conversation tracking
            use_hybrid_search: Whether to use hybrid search
            top_k: Number of documents to retrieve
            temperature: LLM temperature
            
        Returns:
            Response dictionary with answer, sources, and metadata
        """
        try:
            # Step 1: Query Expansion
            expanded_queries = await self._expand_query(query)
            logger.info(f"Expanded query into {len(expanded_queries)} variations")
            
            # Step 2: Multi-query Retrieval
            all_retrieved_docs = []
            
            # Retrieve for original query
            if use_hybrid_search:
                docs = self.vector_store.hybrid_search(query, top_k=top_k)
            else:
                docs = self.vector_store.semantic_search(query, top_k=top_k)
            all_retrieved_docs.extend(docs)
            
            # Retrieve for expanded queries
            for exp_query in expanded_queries[:2]:  # Limit to 2 expansions
                if use_hybrid_search:
                    docs = self.vector_store.hybrid_search(exp_query, top_k=3)
                else:
                    docs = self.vector_store.semantic_search(exp_query, top_k=3)
                all_retrieved_docs.extend(docs)
            
            # Remove duplicates based on embedding_index
            seen_indices = set()
            unique_docs = []
            for doc in all_retrieved_docs:
                idx = doc.get('embedding_index')
                if idx not in seen_indices:
                    seen_indices.add(idx)
                    unique_docs.append(doc)
            
            logger.info(f"Retrieved {len(unique_docs)} unique documents")
            
            # Step 3: Re-ranking (optional, for top documents)
            if len(unique_docs) > top_k:
                reranked_docs = await self._rerank_documents(query, unique_docs, top_k)
            else:
                reranked_docs = unique_docs
            
            # Step 4: Prepare context
            context = self._prepare_context(reranked_docs)
            
            # Step 5: Get conversation history
            conversation_history = self._get_conversation_context(conversation_id)
            
            # Step 6: Generate response
            answer, tokens_used = await self._generate_answer(
                query=query,
                context=context,
                conversation_history=conversation_history,
                temperature=temperature
            )
            
            # Step 7: Extract citations
            sources = self._extract_sources(reranked_docs)
            
            # Step 8: Store in conversation history
            if conversation_id:
                self._add_to_conversation(conversation_id, query, answer)
            else:
                conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self._add_to_conversation(conversation_id, query, answer)
            
            # Determine search strategy
            search_strategy = "hybrid" if use_hybrid_search else "semantic"
            if len(expanded_queries) > 0:
                search_strategy += " + query_expansion"
            
            return {
                'answer': answer,
                'sources': sources,
                'conversation_id': conversation_id,
                'tokens_used': tokens_used,
                'search_strategy': search_strategy
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def _expand_query(self, query: str) -> List[str]:
        """Expand query into related questions"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a query expansion expert."},
                    {"role": "user", "content": self.query_expansion_prompt.format(query=query)}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON array
            try:
                expanded = json.loads(content)
                return expanded if isinstance(expanded, list) else []
            except json.JSONDecodeError:
                # Fallback: just return the original query
                return []
                
        except Exception as e:
            logger.error(f"Error expanding query: {e}")
            return []
    
    async def _rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents using LLM for better relevance
        Note: This is simplified - production would use dedicated re-ranker
        """
        try:
            # For efficiency, only re-rank if we have more than top_k docs
            if len(documents) <= top_k:
                return documents
            
            # Take top candidates (2x top_k) for re-ranking
            candidates = documents[:top_k * 2]
            
            # Simple scoring based on existing scores
            # In production, you'd use a cross-encoder or LLM-based re-ranking
            scored = sorted(
                candidates,
                key=lambda x: x.get('combined_score', x.get('similarity_score', 0)),
                reverse=True
            )
            
            return scored[:top_k]
            
        except Exception as e:
            logger.error(f"Error re-ranking documents: {e}")
            return documents[:top_k]
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.get('source', 'Unknown')
            text = doc.get('text', '')
            score = doc.get('combined_score', doc.get('similarity_score', 0))
            
            context_parts.append(
                f"[Document {i}] (Source: {source}, Relevance: {score:.3f})\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _get_conversation_context(self, conversation_id: Optional[str]) -> str:
        """Get conversation history as context"""
        if not conversation_id or conversation_id not in self.conversations:
            return "No previous conversation."
        
        history = self.conversations[conversation_id]
        
        # Format last 3 exchanges
        recent = history[-6:]  # Last 3 Q&A pairs
        formatted = []
        
        for msg in recent:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    async def _generate_answer(
        self,
        query: str,
        context: str,
        conversation_history: str,
        temperature: float
    ) -> tuple[str, int]:
        """Generate answer using OpenAI"""
        try:
            system_prompt = self.rag_system_prompt.format(
                context=context,
                conversation_history=conversation_history
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return answer, tokens_used
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information for citations"""
        sources = []
        
        for doc in documents:
            source = {
                'source': doc.get('source', 'Unknown'),
                'chunk_index': doc.get('chunk_index', 0),
                'relevance_score': doc.get('combined_score', doc.get('similarity_score', 0)),
                'preview': doc.get('text', '')[:200] + "...",
                'has_financial_keywords': doc.get('has_financial_keywords', False)
            }
            sources.append(source)
        
        return sources
    
    def _add_to_conversation(self, conversation_id: str, query: str, answer: str):
        """Add exchange to conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].extend([
            {'role': 'user', 'content': query, 'timestamp': datetime.now().isoformat()},
            {'role': 'assistant', 'content': answer, 'timestamp': datetime.now().isoformat()}
        ])
        
        # Keep only last 20 messages (10 exchanges)
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get full conversation history"""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation {conversation_id}")
