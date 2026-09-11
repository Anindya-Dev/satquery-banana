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

    def _resolve_api_config(self) -> Dict[str, Optional[str]]:
        is_nvidia_model = self.model_name.startswith("nvidia/") or "/nvidia/" in self.model_name
        api_key = settings.NVIDIA_API_KEY if is_nvidia_model and settings.NVIDIA_API_KEY else settings.OPENAI_API_KEY
        api_base = settings.OPENAI_API_BASE

        if is_nvidia_model and not api_base:
            api_base = settings.NVIDIA_API_BASE_URL

        return {"api_key": api_key, "api_base": api_base or None}

    def _completion_model_name(self) -> str:
        if self.model_name.startswith("nvidia/"):
            return f"openai/{self.model_name}"
        return self.model_name

    def generate_structured_interpretation(
        self,
        request: AnalysisRequest,
        evidence_chain: List[Evidence],
        deterministic_summary: str
    ) -> Dict[str, Any]:
        api_config = self._resolve_api_config()
        api_key = api_config["api_key"]
        if not api_key:
            if not settings.ALLOW_MOCK_FALLBACK:
                return {
                    "summary": deterministic_summary,
                    "claims": [{"claim": deterministic_summary, "evidence_ids": [ev.evidence_id for ev in evidence_chain]}],
                    "insufficient_evidence": False,
                }
            logger.info("LLM API key not configured. Falling back to MockVLMProvider.")
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
                model=self._completion_model_name(),
                messages=messages,
                temperature=0.0,
                api_key=api_key,
                api_base=api_config["api_base"]
            )
            content = response.choices[0].message.content
            return {
                "summary": content,
                "claims": [{"claim": content, "evidence_ids": [ev.evidence_id for ev in evidence_chain]}],
                "insufficient_evidence": False
            }
        except Exception as e:
            if not settings.ALLOW_MOCK_FALLBACK:
                raise
            logger.warning(f"LiteLLM call failed ({str(e)}). Executing mock fallback.")
            return self.mock_fallback.generate_structured_interpretation(request, evidence_chain, deterministic_summary)
