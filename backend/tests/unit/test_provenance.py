import pytest
from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.models import AnalysisRequest

def test_evidence_provenance_chain_integrity():
    router = TaskRouter()
    req = AnalysisRequest(query="Calculate NDVI across Kolkata coastal zones")
    res = router.process(req)
    
    assert res.refusal_triggered is False
    assert len(res.evidence_chain) >= 1
    
    for ev in res.evidence_chain:
        # Provenance invariant: Every evidence item must have full lineage metadata
        assert ev.evidence_id.startswith("EV-")
        assert len(ev.evidence_type) > 0
        assert len(ev.layer) > 0
        assert len(ev.metric_name) > 0
        assert ev.metric_value is not None
        assert ev.evidence_id in res.summary_answer
