import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys & Configurations
    GROQ_API_KEY: str
    MODEL_NAME: str = "openai/gpt-oss-120b"
    
    # Database Configurations
    SQLITE_DB_PATH: str = "creatorops.db"
    CHROMA_PATH: str = "./chroma_db"

    # Konfigurasi Pydantic buat ngebaca file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Abaikan env var lain yang gak didefinisikan di class
    )

# Instantiate singleton object biar bisa di-import di file lain
settings = Settings()

# Test kecil buat mastiin config jalan pas file di-run langsung
if __name__ == "__main__":
    print("✅ Configuration Loaded Successfully!")
    print(f"Model Target    : {settings.MODEL_NAME}")
    print(f"SQLite DB Path  : {settings.SQLITE_DB_PATH}")
    print(f"Chroma DB Path  : {settings.CHROMA_PATH}")
    print(f"Groq API Key status: {'LOADED' if settings.GROQ_API_KEY else 'MISSING'}")