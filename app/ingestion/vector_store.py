"""
Qdrant vector store module.

Handles:
  - Collection creation with proper vector config
  - Upserting chunked documents with embeddings and metadata
  - Payload indexing for RBAC role-based filtering
"""

import uuid
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)
from langchain_core.documents import Document

from app.core.config import settings
from app.ingestion.embedder import get_embedding_model


# ── Qdrant client singleton ────────────────────────────────────────────
_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """Return the shared Qdrant client instance."""
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url)
    return _client


def ensure_collection(vector_size: int = 384) -> None:
    """
    Create the Qdrant collection if it doesn't already exist.

    Parameters
    ----------
    vector_size : int
        Dimension of the embedding vectors (384 for all-MiniLM-L6-v2).
    """
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection_name

    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        print(f"Collection '{collection_name}' already exists — skipping creation.")
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    # Create payload indexes for fast RBAC filtering
    client.create_payload_index(
        collection_name=collection_name,
        field_name="role",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="contains_pii",
        field_schema=PayloadSchemaType.BOOL,
    )

    print(f"✅  Created collection '{collection_name}' (dim={vector_size}, cosine)")
    print("   Indexed payload fields: role, contains_pii")


def upsert_documents(chunks: List[Document], batch_size: int = 64) -> int:
    """
    Embed and upsert document chunks into the Qdrant collection.

    Parameters
    ----------
    chunks : list[Document]
        Chunked documents from the chunker module.
    batch_size : int
        Number of points to upsert per batch.

    Returns
    -------
    int
        Total number of points upserted.
    """
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection_name
    embedder = get_embedding_model()

    ensure_collection()

    total_upserted = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [doc.page_content for doc in batch]

        # Generate embeddings for the batch
        vectors = embedder.embed_documents(texts)

        points = []
        for doc, vector in zip(batch, vectors):
            point_id = str(uuid.uuid4())
            payload = {
                "page_content": doc.page_content,
                **doc.metadata,
            }
            points.append(
                PointStruct(id=point_id, vector=vector, payload=payload)
            )

        client.upsert(collection_name=collection_name, points=points)
        total_upserted += len(points)
        print(f"  Upserted batch {i // batch_size + 1}: {len(points)} points")

    print(f"\n✅  Total points upserted: {total_upserted}")
    return total_upserted


def get_collection_info() -> dict:
    """Return basic info about the current collection."""
    client = get_qdrant_client()
    info = client.get_collection(settings.qdrant_collection_name)
    return {
        "name": settings.qdrant_collection_name,
        "points_count": info.points_count,
        "status": info.status.value,
    }
