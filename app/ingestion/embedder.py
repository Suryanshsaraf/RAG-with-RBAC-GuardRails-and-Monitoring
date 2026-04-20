"""
Embedding generation module.

Provides a singleton HuggingFace embedding model instance used across
the ingestion and retrieval pipelines.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings

# ── Singleton embedding model ──────────────────────────────────────────
_embeddings_instance = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Return the shared HuggingFace embedding model instance.

    Lazy-loaded on first call, then cached for the process lifetime.
    Uses the model specified in ``settings.embedding_model_name``
    (default: sentence-transformers/all-MiniLM-L6-v2, dim=384).

    Returns
    -------
    HuggingFaceEmbeddings
        A LangChain-compatible embedding model.
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        print(f"Loading embedding model: {settings.embedding_model_name}")
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=settings.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings_instance
