"""
Guardrails Manager.

Integrates NeMo Guardrails with the RAG pipeline.
"""

import os
from typing import Dict, Optional

from nemoguardrails import RailsConfig, LLMRails
from app.core.config import settings


from app.guardrails.pii import get_pii_scrubber


class GuardrailsManager:
    """Manages AI Guardrails using NeMo Guardrails."""

    def __init__(self, config_path: str = "app/guardrails/config"):
        self.config = RailsConfig.from_path(config_path)
        self.rails = LLMRails(self.config)
        self.pii_scrubber = get_pii_scrubber()

    async def check_input(self, text: str) -> Optional[str]:
        """
        Check if the input violates any rails.
        Returns a refusal message if violated, else None.
        """
        # 1. PII Scrubbing (pre-emptive)
        # Note: We scrub BEFORE sending to LLM to prevent PII leakage.
        clean_text = self.pii_scrubber.scrub(text)
        
        # 2. NeMo Rails
        response = await self.rails.generate_async(prompt=clean_text)
        
        # If the bot returned a refusal message defined in .co
        if response in [
            "I am sorry, but I can only answer questions related to company documents and policies.",
            "I cannot comply with this request as it violates safety guidelines.",
            "I cannot answer this as it contains inappropriate or toxic content."
        ]:
            return response
        return None

    async def apply_to_rag(self, question: str, rag_engine_query_func) -> Dict:
        """
        Apply guardrails to a RAG query.
        """
        # 1. Pre-retrieval Check (Jailbreak/Off-topic/Toxic)
        violation = await self.check_input(question)
        if violation:
            return {
                "answer": violation,
                "source_documents": [],
                "guardrail_triggered": True
            }

        # 2. Execute RAG
        result = rag_engine_query_func(question)
        
        # 3. Post-generation Check (PII Scrubbing on Answer)
        result["answer"] = self.pii_scrubber.scrub(result["answer"])
        
        return {
            **result,
            "guardrail_triggered": False
        }
