"""
Guardrails Manager.

Integrates NeMo Guardrails with the RAG pipeline.
"""

import os
from typing import Dict, Optional

from nemoguardrails import RailsConfig, LLMRails
from app.core.config import settings


class GuardrailsManager:
    """Manages AI Guardrails using NeMo Guardrails."""

    def __init__(self, config_path: str = "app/guardrails/config"):
        self.config = RailsConfig.from_path(config_path)
        self.rails = LLMRails(self.config)

    async def check_input(self, text: str) -> Optional[str]:
        """
        Check if the input violates any rails.
        Returns a refusal message if violated, else None.
        """
        # Note: NeMo Rails usually handles the full interaction.
        # Here we use it for specific checks.
        response = await self.rails.generate_async(prompt=text)
        
        # If the bot returned a refusal message defined in .co
        if response in [
            "I am sorry, but I can only answer questions related to company documents and policies.",
            "I cannot comply with this request as it violates safety guidelines."
        ]:
            return response
        return None

    async def apply_to_rag(self, question: str, rag_engine_query_func) -> Dict:
        """
        Apply guardrails to a RAG query.
        """
        # 1. Pre-retrieval Check (Jailbreak/Off-topic)
        violation = await self.check_input(question)
        if violation:
            return {
                "answer": violation,
                "source_documents": [],
                "guardrail_triggered": True
            }

        # 2. Execute RAG
        # Note: In a production app, we would pipe the RAG context 
        # into NeMo for hallucination checks.
        result = rag_engine_query_func(question)
        
        # 3. Post-generation Check (Hallucination/PII)
        # For now, we return the RAG result.
        # (Hallucination check requires valid LLM keys to work within NeMo)
        
        return {
            **result,
            "guardrail_triggered": False
        }
