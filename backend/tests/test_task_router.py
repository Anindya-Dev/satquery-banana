from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.models import AnalysisRequest, TaskType

def test_task_router_vqa():
    router = TaskRouter()
    req = AnalysisRequest(
        query="Calculate mean NDVI reflectance across high altitude canopy zones.",
        task_type=TaskType.VQA
    )
    res = router.process(req)
    assert res.refusal_triggered is False
    assert len(res.evidence_chain) >= 2
    assert res.confidence.rating in ["HIGH", "MEDIUM"]
    assert "NDVI" in res.summary_answer

def test_task_router_change_detection():
    router = TaskRouter()
    req = AnalysisRequest(
        query="Detect water body extent changes and compute NDWI delta after heavy rainfall.",
        task_type=TaskType.CHANGE_DETECTION
    )
    res = router.process(req)
    assert res.refusal_triggered is False
    assert res.change_map is not None
    assert res.change_map.changed_area_sq_km > 0
    assert res.coregistration is not None

def test_task_router_grounding():
    router = TaskRouter()
    req = AnalysisRequest(
        query="Segment commercial aircraft and compute runway bounding polygon.",
        task_type=TaskType.GROUNDING
    )
    res = router.process(req)
    assert res.refusal_triggered is False
    assert len(res.grounding_masks) > 0
    assert res.grounding_masks[0].confidence >= 0.90

def test_task_router_refusal_non_geo():
    router = TaskRouter()
    req = AnalysisRequest(
        query="tell a joke about cats",
        task_type=TaskType.AUTO_CLASSIFIED
    )
    res = router.process(req)
    assert res.refusal_triggered is True
    assert "geospatial" in res.refusal_reason.lower()
