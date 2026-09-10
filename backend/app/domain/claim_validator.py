from typing import List, Tuple, Optional
import re
from backend.app.domain.models import Evidence, CoRegistrationQuality, ImageMetadata
from backend.app.domain.sufficiency import EvidenceSufficiencyGate

class RefusalEngine:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore (the )?satellite evidence",
        r"ignore (all )?previous instructions",
        r"assume the image contains",
        r"disregard safety rules"
    ]

    @classmethod
    def evaluate_gates(
        cls,
        query: str,
        images: List[ImageMetadata] = [],
        valid_pixel_ratio: float = 1.0,
        coregistration: Optional[CoRegistrationQuality] = None
    ) -> Tuple[bool, Optional[str]]:
        query_lower = query.lower()

        # Gate 1: Prompt Injection Check
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, query_lower):
                return True, f"Refusal Triggered: Prompt injection attempt detected ('{query}'). Refusing ungrounded evaluation."

        # Gate 2: Out-of-domain generic chat query check
        non_geo_keywords = ["write a poem", "tell a joke", "recipe for cake", "who won the election"]
        for kw in non_geo_keywords:
            if kw in query_lower:
                return True, f"Refusal Triggered: Query '{query}' is outside the domain of geospatial remote sensing intelligence."

        # Gate 3: Evidence Sufficiency Gate
        is_sufficient, reason = EvidenceSufficiencyGate.evaluate_sufficiency(
            images=images,
            valid_pixel_ratio=valid_pixel_ratio,
            coregistration=coregistration
        )
        if not is_sufficient:
            return True, reason

        return False, None

class ClaimValidator:
    UNSUPPORTED_CAUSAL_WORDS = [
        "drought caused", "deforestation caused", "pollution caused",
        "factory dumping caused", "climate change caused", "illegal dumping caused"
    ]

    @classmethod
    def validate_and_ground(cls, text_claim: str, evidence_chain: List[Evidence]) -> str:
        if not evidence_chain:
            return f"[GROUNDING WARNING: Zero deterministic evidence gathered. Refusing ungrounded claim] {text_claim}"

        clean_claim = text_claim
        claim_lower = clean_claim.lower()

        # 1. Block unsupported causal leaps
        for causal_word in cls.UNSUPPORTED_CAUSAL_WORDS:
            if causal_word in claim_lower:
                clean_claim = re.sub(
                    re.escape(causal_word),
                    "correlated with observed spectral shift (uncertain causality: requires ground-truth validation)",
                    clean_claim,
                    flags=re.IGNORECASE
                )

        # 2. Detect contradictory evidence in evidence chain
        contradiction_warning = ""
        deltas = [ev.metric_value for ev in evidence_chain if isinstance(ev.metric_value, (int, float))]
        diff_evs = [ev for ev in evidence_chain if "diff" in ev.metric_name.lower() or "delta" in ev.metric_name.lower()]
        if len(diff_evs) >= 2:
            vals = [ev.metric_value for ev in diff_evs if isinstance(ev.metric_value, (int, float))]
            if any(v > 0 for v in vals) and any(v < 0 for v in vals):
                contradiction_warning = " [CONTRADICTORY EVIDENCE DETECTED: Conflicting trend metrics observed across evidence chain]"

        # 3. Check for unsupported numerical/area claims when evidence lacks water/area metrics
        has_area_ev = any(ev.metric_name in ["Inundated_Area", "Grounded_Area", "NDWI_mean"] for ev in evidence_chain)
        if "flooded" in claim_lower and "hectare" in claim_lower and not has_area_ev:
            clean_claim = "[GROUNDING REFUSAL: Insufficient water evidence to quantify flooded area] " + clean_claim

        # 4. Check for fake/missing citations & attach verified evidence IDs
        citations = [ev.evidence_id for ev in evidence_chain if ev.evidence_id]
        if not citations:
            return f"[GROUNDING REFUSAL: No valid evidence ID present] {clean_claim}"

        citation_str = f" [Verified via Evidence: {', '.join(citations[:3])}]"
        
        if citation_str not in clean_claim:
            return f"{clean_claim}{contradiction_warning}{citation_str}"
        return f"{clean_claim}{contradiction_warning}"
