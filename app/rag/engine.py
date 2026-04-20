"""
RAG Engine.

Orchestrates retrieval and generation.
"""

from typing import Dict, List, Optional, Tuple

from langchain_core.documents import Document

from app.rag.retriever import search
from app.rag.generator import get_rag_chain, format_docs
from app.guardrails.manager import GuardrailsManager


class RAGEngine:
    """Enterprise RAG Engine with RBAC and Guardrails."""

    def __init__(self):
        self.chain = get_rag_chain()
        self.guardrails = GuardrailsManager()

    async def query(
        self, 
        question: str, 
        role: str = "general", 
        top_k: int = 5
    ) -> Dict:
        """
        Execute a full RAG query: Guardrails (Input) → Retrieve → Generate → Guardrails (Output).

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
            Contains 'answer', 'source_documents', and metadata.
        """
        # 1. Input Guardrails (Pre-retrieval)
        violation = await self.guardrails.check_input(question)
        if violation:
            return {
                "answer": violation,
                "source_documents": [],
                "guardrail_triggered": True
            }

        # 2. Retrieve
        docs = search(question, top_k=top_k, role_filter=role)
        
        # 2. Check if anything was found
        if not docs or (len(docs) > 0 and docs[0].metadata.get("score", 0) < 0.01):
            return {
                "answer": "I don't know the answer to that based on the available documents. I don't have access to information outside the provided context.",
                "source_documents": docs
            }
        
        # 3. Format Context
        context = format_docs(docs)
        
        # 4. Generate
        answer = self.chain.invoke({
            "context": context,
            "question": question
        })
        
        # 5. Output Guardrails (PII Scrubbing on Answer)
        clean_answer = self.pii_scrubber.scrub(answer) if hasattr(self, 'pii_scrubber') else self.guardrails.pii_scrubber.scrub(answer)
        
        return {
            "answer": clean_answer,
            "source_documents": docs,
            "guardrail_triggered": False
        }


def get_rag_engine() -> RAGEngine:
    """Singleton RAG Engine."""
    return RAGEngine()
