# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

**GET /**

Returns system health and statistics.

**Response:**
```json
{
  "status": "healthy",
  "vector_store_documents": 150,
  "cache_size": 12,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Upload Document

**POST /upload**

Upload a document for processing and indexing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary)

**Supported formats:** PDF, DOCX, TXT

**Response:**
```json
{
  "document_id": "doc_20240115_103000_earnings_q4.pdf",
  "filename": "earnings_q4.pdf",
  "chunks_created": 45,
  "status": "success",
  "message": "Successfully processed earnings_q4.pdf into 45 chunks"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file type
- 500: Processing error

---

### Query Documents

**POST /query**

Query the RAG system with a question.

**Request:**
```json
{
  "query": "What was the revenue growth in Q4?",
  "conversation_id": "conv_20240115_103000",
  "use_hybrid_search": true,
  "top_k": 5,
  "temperature": 0.7
}
```

**Parameters:**
- `query` (required): User's question
- `conversation_id` (optional): For conversation continuity
- `use_hybrid_search` (optional): Use hybrid search (default: true)
- `top_k` (optional): Number of documents to retrieve (default: 5)
- `temperature` (optional): LLM temperature (default: 0.7)

**Response:**
```json
{
  "answer": "According to the Q4 earnings report, revenue grew by 15% year-over-year...",
  "sources": [
    {
      "source": "earnings_q4.pdf",
      "chunk_index": 3,
      "relevance_score": 0.89,
      "preview": "Revenue increased from $45M to $52M...",
      "has_financial_keywords": true
    }
  ],
  "conversation_id": "conv_20240115_103000",
  "tokens_used": 450,
  "processing_time": 2.3,
  "search_strategy": "hybrid + query_expansion"
}
```

**Status Codes:**
- 200: Success
- 500: Processing error

---

### List Documents

**GET /documents**

List all documents in the vector store.

**Response:**
```json
{
  "total_documents": 3,
  "documents": [
    {
      "source": "earnings_q4.pdf",
      "chunk_count": 45,
      "added_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Delete Document

**DELETE /documents/{document_id}**

Delete a document from the vector store.

**Path Parameters:**
- `document_id`: Document identifier (source filename)

**Response:**
```json
{
  "status": "success",
  "message": "Deleted document earnings_q4.pdf"
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Deletion error

---

### Get Conversation History

**GET /conversations/{conversation_id}**

Retrieve conversation history.

**Path Parameters:**
- `conversation_id`: Conversation identifier

**Response:**
```json
{
  "conversation_id": "conv_20240115_103000",
  "message_count": 6,
  "history": [
    {
      "role": "user",
      "content": "What was the revenue?",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Revenue was $52M...",
      "timestamp": "2024-01-15T10:30:03Z"
    }
  ]
}
```

---

### Clear Conversation

**POST /conversations/{conversation_id}/clear**

Clear conversation history.

**Path Parameters:**
- `conversation_id`: Conversation identifier

**Response:**
```json
{
  "status": "success",
  "message": "Cleared conversation conv_20240115_103000"
}
```

---

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## Rate Limiting

Currently no rate limiting. For production deployment, implement rate limiting per IP/user.

## Authentication

Currently no authentication required. For production deployment, add API key authentication.
