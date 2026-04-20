"""
Centralized configuration for the EnterpriseRAG application.

Loads all environment variables from .env and exposes them as typed attributes
via a Pydantic Settings model.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- LLM Provider Keys ---
    groq_api_key: str = Field(default="", description="Groq API key for Llama models")
    openai_api_key: str = Field(default="", description="OpenAI API key (fallback LLM)")

    # --- LangSmith Monitoring ---
    langchain_api_key: str = Field(default="", description="LangSmith API key")
    langchain_tracing_v2: bool = Field(default=True, description="Enable LangSmith tracing")
    langchain_project: str = Field(default="EnterpriseRAG", description="LangSmith project name")

    # --- Authentication ---
    jwt_secret_key: str = Field(default="supersecretkey123", description="JWT signing secret")
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expiration_minutes: int = Field(default=60, description="JWT token TTL in minutes")

    # --- Qdrant Vector Database ---
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant REST URL")
    qdrant_collection_name: str = Field(default="enterprise_docs", description="Qdrant collection name")

    # --- Embedding Model ---
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model identifier",
    )

    # --- LLM Model ---
    llm_model_name: str = Field(default="llama-3.1-8b-instant", description="LLM model name")
    llm_provider: str = Field(default="groq", description="LLM provider (groq | openai)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance — import this everywhere
settings = Settings()
