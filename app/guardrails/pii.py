"""
PII Scrubbing module.

Uses Microsoft Presidio to detect and anonymize PII in text.
"""

from typing import List, Optional

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PIIScrubber:
    """Handles PII detection and anonymization."""

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        # Default entities to scrub
        self.default_entities = [
            "PHONE_NUMBER", 
            "EMAIL_ADDRESS", 
            "CREDIT_CARD", 
            "LOCATION", 
            "PERSON", 
            "US_SSN",
            "US_PASSPORT",
            "IP_ADDRESS"
        ]

    def scrub(self, text: str, entities: Optional[List[str]] = None) -> str:
        """
        Anonymize PII in the given text.
        """
        if not text:
            return text

        # 1. Analyze
        results = self.analyzer.analyze(
            text=text, 
            entities=entities or self.default_entities, 
            language='en'
        )

        # 2. Anonymize
        # We can customize operators if needed, e.g., mask with '<PII>'
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
            }
        )

        return anonymized_result.text


# Singleton instance
_scrubber: Optional[PIIScrubber] = None

def get_pii_scrubber() -> PIIScrubber:
    """Return the shared PII scrubber instance."""
    global _scrubber
    if _scrubber is None:
        _scrubber = PIIScrubber()
    return _scrubber
