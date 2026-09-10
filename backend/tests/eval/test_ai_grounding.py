from backend.app.orchestration.task_router import TaskRouter
from backend.app.domain.models import AnalysisRequest, TaskType

EVAL_BENCHMARK = [
    {
        "query": "Show turbid water near Kolkata in the last 30 days.",
        "expected_task": TaskType.CHANGE_DETECTION,
        "should_refuse": False
    },
    {
        "query": "Segment commercial aircraft and runway near Delhi Airport.",
        "expected_task": TaskType.GROUNDING,
        "should_refuse": False
    },
    {
        "query": "Apply 5x5 Enhanced Lee filter on Assam SAR images.",
        "expected_task": TaskType.OPTICAL_SAR_FUSION,
        "should_refuse": False
    },
    {
        "query": "Calculate mean NDVI reflectance across Western Ghats.",
        "expected_task": TaskType.VQA,
        "should_refuse": False
    },
    {
        "query": "tell a joke about funny dogs",
        "expected_task": TaskType.AUTO_CLASSIFIED,
        "should_refuse": True
    }
]

def test_ai_grounding_eval_suite():
    router = TaskRouter()
    passed_count = 0
    
    for item in EVAL_BENCHMARK:
        req = AnalysisRequest(query=item["query"])
        res = router.process(req)
        
        if item["should_refuse"]:
            assert res.refusal_triggered is True
            assert "geospatial" in res.refusal_reason.lower()
        else:
            assert res.refusal_triggered is False
            assert len(res.evidence_chain) >= 1
            assert "Verified via Evidence" in res.summary_answer
        
        passed_count += 1

    assert passed_count == len(EVAL_BENCHMARK)
