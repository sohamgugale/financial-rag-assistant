import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application settings
    APP_NAME: str = "Financial Research Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # Vector database settings
    VECTOR_DB_PATH: str = "vector_store"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # LLM settings
    MODEL_NAME: str = "claude-3-5-sonnet-20241022"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1500
    
    # Retrieval settings
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

settings = Settings()
