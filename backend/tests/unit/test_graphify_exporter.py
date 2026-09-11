import pytest
from backend.app.domain.graphify_exporter import GraphifyExporter
from backend.app.api.routes import export_graphify_knowledge_graph


def test_graphify_exporter_basic_structure():
    exporter = GraphifyExporter(query_text="Compute NDWI for Kolkata water bodies", query_id="q-test-101")
    
    mock_result = {
        "location_name": "Kolkata, West Bengal",
        "bbox": [88.2, 22.4, 88.5, 22.7],
        "candidate_tiles": [
            {
                "tile_id": "tile-s2-kolkata-01",
                "sensor": "Sentinel-2 MSI",
                "acquisition_time": "2024-05-20",
                "cloud_cover": 2.5,
                "metrics": {
                    "ndwi": 0.4852,
                    "ndvi": 0.2104
                }
            }
        ],
        "evidence_chain": [
            {
                "evidence_id": "ev-881",
                "description": "NDWI surface water reflectance metric derived via Sentinel-2 band math."
            }
        ],
        "validated_claims": [
            {
                "claim": "Water surface area increased by 14.2% following precipitation.",
                "confidence": 0.96
            }
        ],
        "confidence": 0.96
    }
    
    graph = exporter.export_analysis_graph(mock_result)
    
    assert graph["graphify_version"] == "0.9.58"
    assert graph["query_id"] == "q-test-101"
    assert graph["stats"]["node_count"] >= 5
    assert graph["stats"]["edge_count"] >= 4
    
    node_types = {n["type"] for n in graph["nodes"]}
    assert "QUERY" in node_types
    assert "LOCATION" in node_types
    assert "TILE" in node_types
    assert "SPECTRAL_METRIC" in node_types
    assert "EVIDENCE" in node_types
    assert "CLAIM" in node_types
    assert "CONFIDENCE" in node_types


def test_graphify_endpoint_handling():
    data = {
        "query_text": "Identify built up expansion in Bhubaneswar",
        "location_name": "Bhubaneswar",
        "confidence": 0.92,
        "claims": ["Impervious surface area enlarged by 3.8 km2."]
    }
    
    res = export_graphify_knowledge_graph(request=None, data=data)
    assert "nodes" in res
    assert "edges" in res
    assert res["stats"]["node_count"] > 0
