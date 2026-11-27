from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CreatorOps AI Agent"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # AI & API Keys
    GROQ_API_KEY: str
    LLM_MODEL: str = "openai/gpt-oss-120b"
    
    # Database Paths
    SQLITE_DB_PATH: str = "creatorops.db"
    CHROMA_DB_PATH: str = "./chroma_db"  # <-- INI YANG TADI KURANG BRO!

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()