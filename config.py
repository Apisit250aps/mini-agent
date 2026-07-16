from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings loaded from environment variables and .env file."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DB: str = "mini_agent"
    MONGODB_COLLECTION: str = "embeddings"
    MONGODB_MEMORY_COLLECTION: str = "memories"
    MONGODB_CHAT_COLLECTION: str = "chat_logs"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Module-level aliases for direct access
OLLAMA_BASE_URL: str = settings.OLLAMA_BASE_URL
OLLAMA_API_KEY: str = settings.OLLAMA_API_KEY
OLLAMA_MODEL: str = settings.OLLAMA_MODEL
OLLAMA_EMBED_MODEL: str = settings.OLLAMA_EMBED_MODEL
MONGODB_URI: str = settings.MONGODB_URI
MONGODB_DB: str = settings.MONGODB_DB
MONGODB_COLLECTION: str = settings.MONGODB_COLLECTION
MONGODB_MEMORY_COLLECTION: str = settings.MONGODB_MEMORY_COLLECTION
MONGODB_CHAT_COLLECTION: str = settings.MONGODB_CHAT_COLLECTION
