from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from backend.app.domain.models import AnalysisRequest, AnalysisResult, TaskType
from backend.app.orchestration.task_router import TaskRouter
from backend.app.workers.job_queue import job_manager
from backend.app.core.exceptions import InsufficientEvidenceError
from backend.app.geospatial.geocoder import Geocoder
from backend.app.storage.metadata_db import metadata_db

router = APIRouter()
task_router = TaskRouter()

@router.get("/health")
def get_health() -> Dict[str, Any]:
    """Readiness and Liveness Health Check Endpoint."""
    return {
        "status": "healthy",
        "service": "SatQuery AI Backend Engine",
        "version": "1.0.0",
        "liveness": True,
        "readiness": True,
        "active_specialists": [
            "VQASpecialist",
            "GroundingSpecialist",
            "ChangeDetectionSpecialist",
            "OpticalSARFusionSpecialist"
        ],
        "refusal_gates": ["CloudCoverGate", "CoRegistrationGate", "DomainBoundGate", "EvidenceSufficiencyGate"]
    }

@router.post("/analyze", response_model=AnalysisResult)
def analyze_query(request: AnalysisRequest) -> AnalysisResult:
    """Synchronous natural-language query analysis endpoint."""
    import json
    import time
    from backend.app.core.config import settings
    
    key = ""
    now = time.time()
    try:
        key = json.dumps(request.model_dump(mode="json"), sort_keys=True)
        cached = metadata_db.get_cached_response(key, now)
        if cached:
            return AnalysisResult.model_validate(cached)
    except Exception:
        pass

    result = task_router.process(request)

    if key:
        try:
            metadata_db.cache_response(key, result.model_dump(mode="json"), now + settings.RESPONSE_CACHE_TTL_SECONDS)
        except Exception:
            pass

    return result

@router.get("/geocode")
def geocode_place(q: str) -> List[Dict[str, object]]:
    return Geocoder.search(q)

@router.post("/jobs")
def submit_analysis_job(request: AnalysisRequest) -> Dict[str, Any]:
    """Asynchronous analysis job submission endpoint."""
    job_id = job_manager.submit_job(
        task_type=request.task_type.value if request.task_type else "AnalysisJob",
        func=task_router.process,
        request=request
    )
    return {"job_id": job_id, "status": "PENDING", "message": "Analysis job submitted successfully."}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Asynchronous job status check endpoint."""
    status = job_manager.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return status

@router.get("/scenarios")
def get_evaluator_scenarios() -> List[Dict[str, Any]]:
    """Official 5 SIH Evaluator Scenarios."""
    return [
        {
            "id": "scenario-1",
            "title": "Kolkata Coastal Inundation",
            "sensor": "Sentinel-2 MSI",
            "date": "2024-05-20",
            "query": "Detect water body extent changes and compute NDWI delta after heavy rainfall.",
            "task_type": TaskType.CHANGE_DETECTION,
            "target_region": "Kolkata, WB (22.57° N, 88.36° E)",
            "expected_confidence": 0.96
        },
        {
            "id": "scenario-2",
            "title": "Bhubaneswar Urban Expansion",
            "sensor": "Landsat-9 OLI",
            "date": "2023-11-14",
            "query": "Identify new impervious surface structures and compute NDBI built-up index.",
            "task_type": TaskType.VQA,
            "target_region": "Bhubaneswar, Odisha",
            "expected_confidence": 0.92
        },
        {
            "id": "scenario-3",
            "title": "Assam Flood SAR Penetration",
            "sensor": "Sentinel-1 SAR C-Band",
            "date": "2024-07-02",
            "query": "Apply 5x5 Enhanced Lee speckle filter and map inundated regions through cloud cover.",
            "task_type": TaskType.OPTICAL_SAR_FUSION,
            "target_region": "Kaziranga / Brahmaputra Basin",
            "expected_confidence": 0.98
        },
        {
            "id": "scenario-4",
            "title": "Delhi Airport Runway Visual Grounding",
            "sensor": "WorldView-3 (0.3m)",
            "date": "2024-02-10",
            "query": "Segment commercial aircraft and compute runway bounding polygon.",
            "task_type": TaskType.GROUNDING,
            "target_region": "IGI Airport, New Delhi",
            "expected_confidence": 0.96
        },
        {
            "id": "scenario-5",
            "title": "Western Ghats Forest Health Index",
            "sensor": "Sentinel-2 MSI",
            "date": "2024-01-18",
            "query": "Calculate mean NDVI reflectance across high altitude canopy zones.",
            "task_type": TaskType.VQA,
            "target_region": "Western Ghats, MH",
            "expected_confidence": 0.94
        }
    ]

@router.post("/graphify")
def export_graphify_knowledge_graph(request: Optional[AnalysisRequest] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate Graphify Knowledge Graph JSON for satellite query evidence and topology."""
    from backend.app.domain.graphify_exporter import GraphifyExporter

    query_text = "Satellite Imagery Query Analysis"
    analysis_dict = {}

    if data and "nodes" in data and "edges" in data:
        return data

    if data:
        analysis_dict = data
        query_text = data.get("query_text", data.get("query", query_text))

    if request:
        query_text = request.query
        result = task_router.process(request)
        analysis_dict = result.model_dump(mode="json")

    exporter = GraphifyExporter(query_text=query_text)
    return exporter.export_analysis_graph(analysis_dict)

