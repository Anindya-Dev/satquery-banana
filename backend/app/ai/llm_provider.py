import os
import json
from typing import List, Dict, Any, Optional
from backend.app.ai.base import VisionLanguageProvider
from backend.app.domain.models import AnalysisRequest, Evidence
from backend.app.core.config import settings
from backend.app.core.logging import logger

class MockVLMProvider(VisionLanguageProvider):
    def __init__(self):
        super().__init__(provider_name="Mock Grounded VLM Provider")

    def generate_structured_interpretation(
        self,
        request: AnalysisRequest,
        evidence_chain: List[Evidence],
        deterministic_summary: str
    ) -> Dict[str, Any]:
        citations = [ev.evidence_id for ev in evidence_chain]
        return {
            "summary": deterministic_summary,
            "claims": [
                {
                    "claim": f"Derived raster analysis confirms measured parameters for query '{request.query}'.",
                    "evidence_ids": citations
                }
            ],
            "insufficient_evidence": False
        }

class OpenAIProvider(VisionLanguageProvider):
    def __init__(self, model_name: Optional[str] = None):
        super().__init__(provider_name="OpenAI / LiteLLM Provider")
        self.model_name = model_name or settings.LITELLM_MODEL
        self.mock_fallback = MockVLMProvider()

    def generate_structured_interpretation(
        self,
        request: AnalysisRequest,
        evidence_chain: List[Evidence],
        deterministic_summary: str
    ) -> Dict[str, Any]:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.info("OPENAI_API_KEY not configured. Falling back to MockVLMProvider.")
            return self.mock_fallback.generate_structured_interpretation(request, evidence_chain, deterministic_summary)

        try:
            import litellm
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an evidence-grounded remote sensing interpreter. "
                        "Do NOT invent coordinates, dates, or spectral index values. "
                        "Strictly format your answer based on the provided deterministic measurements."
                    )
                },
                {
                    "role": "user",
                    "content": f"Query: {request.query}\nEvidence Summary: {deterministic_summary}\nEvidence Chain: {[ev.model_dump() for ev in evidence_chain]}"
                }
            ]
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                temperature=0.0
            )
            content = response.choices[0].message.content
            return {
                "summary": content,
                "claims": [{"claim": content, "evidence_ids": [ev.evidence_id for ev in evidence_chain]}],
                "insufficient_evidence": False
            }
        except Exception as e:
            logger.warning(f"LiteLLM call failed ({str(e)}). Executing mock fallback.")
            return self.mock_fallback.generate_structured_interpretation(request, evidence_chain, deterministic_summary)
