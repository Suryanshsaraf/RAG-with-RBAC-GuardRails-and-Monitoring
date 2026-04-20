"""
RAG Engine.

Orchestrates retrieval and generation.
"""

from typing import Dict, List, Optional, Tuple

from langchain_core.documents import Document

from app.rag.retriever import search
from app.rag.generator import get_rag_chain, format_docs


class RAGEngine:
    """Enterprise RAG Engine with RBAC."""

    def __init__(self):
        self.chain = get_rag_chain()

    def query(
        self, 
        question: str, 
        role: str = "general", 
        top_k: int = 5
    ) -> Dict:
        """
        Execute a full RAG query: Retrieve → Generate.

        Parameters
        ----------
        question : str
            User's natural language question.
        role : str
            RBAC role of the user.
        top_k : int
            Number of documents to retrieve.

        Returns
        -------
        dict
            Contains 'answer' and 'source_documents'.
        """
        # 1. Retrieve
        docs = search(question, top_k=top_k, role_filter=role)
        
        # 2. Format Context
        context = format_docs(docs)
        
        # 3. Generate
        answer = self.chain.invoke({
            "context": context,
            "question": question
        })
        
        return {
            "answer": answer,
            "source_documents": docs
        }


def get_rag_engine() -> RAGEngine:
    """Singleton RAG Engine."""
    return RAGEngine()
