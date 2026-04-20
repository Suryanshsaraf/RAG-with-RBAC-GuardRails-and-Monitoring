"""
RAG Engine.

Orchestrates retrieval and generation.
"""

import json
from typing import Dict, List, Optional, Tuple, Any

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
        top_k: int = 5,
        use_hyde: bool = False,
        multi_query: bool = False
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
        docs = await search(question, top_k=top_k, role_filter=role, use_hyde=use_hyde, multi_query=multi_query)
        
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

    async def stream_query(
        self, 
        question: str, 
        role: str = "general", 
        top_k: int = 5,
        use_hyde: bool = False,
        multi_query: bool = False
    ):
        """
        Execute a streaming RAG query.
        Yields answer chunks as JSON strings.
        """
        # 1. Input Guardrails
        violation = await self.guardrails.check_input(question)
        if violation:
            yield json.dumps({"answer": violation, "guardrail_triggered": True}) + "\n"
            return

        # 2. Retrieve
        docs = await search(question, top_k=top_k, role_filter=role, use_hyde=use_hyde, multi_query=multi_query)
        
        # 3. Check threshold
        if not docs or (len(docs) > 0 and docs[0].metadata.get("score", 0) < 0.01):
            yield json.dumps({
                "answer": "I don't know the answer to that based on the available documents.",
                "guardrail_triggered": False
            }) + "\n"
            return
        
        # 4. Stream Generate
        context = format_docs(docs)
        async for chunk in self.chain.astream({"context": context, "question": question}):
            yield json.dumps({"answer": chunk, "guardrail_triggered": False}) + "\n"
        
        # 5. Final yield with sources
        sources = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in docs
        ]
        yield json.dumps({"sources": sources}) + "\n"


def get_rag_engine() -> RAGEngine:
    """Singleton RAG Engine."""
    return RAGEngine()
