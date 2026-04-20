"""
Reranker module.

Uses FlashRank to rerank retrieved documents.
"""

from typing import List
from flashrank import Ranker, RerankRequest
from langchain_core.documents import Document


class FlashReranker:
    """Fast and lightweight reranker using FlashRank."""

    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2"):
        # This will download the model on first init (~30MB)
        self.ranker = Ranker(model_name=model_name, cache_dir="/tmp/flashrank_cache")

    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
        """
        Rerank a list of documents based on a query.
        """
        if not documents:
            return []

        # Convert LangChain documents to FlashRank format
        passages = []
        for i, doc in enumerate(documents):
            passages.append({
                "id": i,
                "text": doc.page_content,
                "meta": doc.metadata
            })

        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # Reconstruct LangChain documents in new order
        reranked_docs = []
        for res in results[:top_n]:
            # Update score in metadata with reranked score
            meta = res["meta"].copy()
            meta["rerank_score"] = res["score"]
            reranked_docs.append(Document(
                page_content=res["text"],
                metadata=meta
            ))

        return reranked_docs


# Singleton instance
_reranker = None

def get_reranker() -> FlashReranker:
    """Return the shared reranker instance."""
    global _reranker
    if _reranker is None:
        _reranker = FlashReranker()
    return _reranker
