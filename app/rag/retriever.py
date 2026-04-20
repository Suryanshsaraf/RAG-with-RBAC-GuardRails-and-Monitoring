"""
Retriever module.

Provides vector similarity search against the Qdrant collection,
with optional RBAC role-based filtering.
"""

from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from langchain_core.documents import Document

from app.core.config import settings
from app.ingestion.embedder import get_embedding_model
from app.ingestion.vector_store import get_qdrant_client


def search(
    query: str,
    top_k: int = 5,
    role_filter: Optional[str] = None,
) -> List[Document]:
    """
    Perform vector similarity search against the Qdrant collection.

    Parameters
    ----------
    query : str
        The user's natural-language query.
    top_k : int
        Number of results to return.
    role_filter : str, optional
        If provided, only return documents tagged with this RBAC role
        (or 'general' which is accessible to everyone).

    Returns
    -------
    list[Document]
        Matching documents with score in metadata.
    """
    client = get_qdrant_client()
    embedder = get_embedding_model()

    query_vector = embedder.embed_query(query)

    # ── Build optional RBAC filter ──────────────────────────────────
    qdrant_filter = None
    if role_filter:
        # User can see docs matching their role OR 'general' docs
        qdrant_filter = Filter(
            should=[
                FieldCondition(key="role", match=MatchValue(value=role_filter)),
                FieldCondition(key="role", match=MatchValue(value="general")),
            ]
        )

    results = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        query_filter=qdrant_filter,
        limit=top_k,
        with_payload=True,
    ).points

    # ── Convert to LangChain Documents ──────────────────────────────
    documents: List[Document] = []
    for hit in results:
        payload = hit.payload or {}
        page_content = payload.pop("page_content", "")
        metadata = {
            **payload,
            "score": round(hit.score, 4),
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents
