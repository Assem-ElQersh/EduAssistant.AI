from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/ai_education_db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-in-production-make-it-long-and-random"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    
    # RAG System
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    LLM_MODEL: str = "gpt-3.5-turbo"  # fallback to local models if no API key
    HF_MODEL_NAME: str = "microsoft/DialoGPT-medium"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5
    
    # Redis (for caching and sessions)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Japanese Grammar Data
    WASABI_GRAMMAR_URL: str = "https://www.wasabi-jpn.com/japanese-grammar/"
    GRAMMAR_DATA_PATH: str = "data/japanese_grammar"
    
    # Analytics
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90
    
    # Development & CORS
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3004,http://localhost:3005,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
