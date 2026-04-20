"""
Retriever module.

Provides vector similarity search against the Qdrant collection,
with optional RBAC role-based filtering.
"""

from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition, 
    Filter, 
    MatchValue, 
    Prefetch, 
    Fusion, 
    FusionQuery, 
    NearestQuery,
    SparseVector as QdrantSparseVector
)
from langchain_core.documents import Document

from app.core.config import settings
from app.ingestion.embedder import get_embedding_model
from app.ingestion.vector_store import get_qdrant_client, get_sparse_embedder
from app.rag.reranker import get_reranker


from app.rag.expansion import generate_hypothetical_document, rewrite_query


async def search(
    query: str,
    top_k: int = 5,
    role_filter: Optional[str] = None,
    rerank: bool = True,
    use_hyde: bool = False,
    multi_query: bool = False
) -> List[Document]:
    """
    Perform hybrid (dense + sparse) search against the Qdrant collection.
    Optional RBAC, FlashRank reranking, HyDE expansion, and Multi-Query retrieval.
    """
    client = get_qdrant_client()
    embedder = get_embedding_model()
    sparse_embedder = get_sparse_embedder()

    # ── 1. Query Expansion (HyDE or Multi-Query) ──────────────────
    queries = [query]
    
    if multi_query:
        try:
            alternatives = await rewrite_query(query, n=2)
            queries.extend(alternatives)
            # Deduplicate while preserving order
            queries = list(dict.fromkeys(queries))
        except Exception as e:
            print(f"Multi-query expansion failed: {e}")

    # HyDE is applied to the original query if enabled
    if use_hyde:
        try:
            hypothetical_doc = await generate_hypothetical_document(query)
            # We add it as a separate query for retrieval
            queries.append(hypothetical_doc)
        except Exception as e:
            print(f"HyDE expansion failed: {e}")

    all_docs = []
    seen_ids = set()

    # ── 2. Loop through queries (Parallelizable, but simple for now) ──
    for q in queries:
        # Generate Vectors
        dense_vector = embedder.embed_query(q)
        sparse_vector_gen = sparse_embedder.embed([q])
        sparse_vector = next(sparse_vector_gen)

        # Build optional RBAC filter
        qdrant_filter = None
        if role_filter and role_filter.lower() != "admin":
            qdrant_filter = Filter(
                should=[
                    FieldCondition(key="role", match=MatchValue(value=role_filter)),
                    FieldCondition(key="role", match=MatchValue(value="general")),
                ]
            )

        # Perform Hybrid Search with RRF
        fetch_k = top_k * 2 if rerank else top_k
        
        results = client.query_points(
            collection_name=settings.qdrant_collection_name,
            prefetch=[
                Prefetch(
                    query=NearestQuery(nearest=dense_vector),
                    using="",
                    limit=fetch_k,
                    filter=qdrant_filter,
                ),
                Prefetch(
                    query=NearestQuery(
                        nearest=QdrantSparseVector(
                            indices=sparse_vector.indices.tolist(),
                            values=sparse_vector.values.tolist(),
                        )
                    ),
                    using="text-sparse",
                    limit=fetch_k,
                    filter=qdrant_filter,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=fetch_k,
            with_payload=True,
        ).points

        # Parse and deduplicate
        for hit in results:
            # We use a hash of the content as ID since we don't store point IDs in Document
            content = hit.payload.get("page_content", "")
            content_hash = hash(content)
            
            if content_hash not in seen_ids:
                seen_ids.add(content_hash)
                payload = hit.payload or {}
                metadata = {
                    **payload,
                    "score": round(hit.score, 4),
                }
                # Remove large payload from metadata to keep it clean
                metadata.pop("page_content", None)
                
                all_docs.append(Document(page_content=content, metadata=metadata))

    # ── 3. Optional Reranking Step ──────────────────────────────────
    if rerank and all_docs:
        reranker = get_reranker()
        # Rerank against original query
        all_docs = reranker.rerank(query, all_docs, top_n=top_k)

    return all_docs[:top_k]
