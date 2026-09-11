"""
Graphify Exporter Module for SatQuery AI.

Converts structured queries, satellite scene tiles, spectral index calculations,
evidence objects, and validated AI claims into canonical Graphify Node-Edge JSON graph format.
"""

from typing import Dict, List, Any, Optional
import math


class GraphifyExporter:
    """
    Transforms SatQuery analytical evidence and spatial-spectral objects
    into a queryable, visualizable Knowledge Graph topology.
    """

    NODE_TYPES = {
        "QUERY": "#3B82F6",         # Blue
        "LOCATION": "#10B981",      # Emerald Green
        "TILE": "#8B5CF6",          # Violet
        "SPECTRAL_METRIC": "#F59E0B",# Amber
        "EVIDENCE": "#06B6D4",      # Cyan
        "CLAIM": "#EC4899",         # Pink
        "CONFIDENCE": "#6366F1",    # Indigo
    }

    def __init__(self, query_text: str = "", query_id: str = "q-001"):
        self.query_text = query_text or "Satellite Imagery Query"
        self.query_id = query_id
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self._node_ids = set()

    def add_node(self, node_id: str, label: str, node_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a unique node to the knowledge graph."""
        if node_id in self._node_ids:
            return node_id
        
        color = self.NODE_TYPES.get(node_type.upper(), "#9CA3AF")
        node_obj = {
            "id": node_id,
            "label": label,
            "type": node_type.upper(),
            "color": color,
            "metadata": metadata or {}
        }
        self.nodes.append(node_obj)
        self._node_ids.add(node_id)
        return node_id

    def add_edge(self, source_id: str, target_id: str, relationship: str, weight: float = 1.0) -> None:
        """Add a directed edge between two existing nodes."""
        edge_id = f"{source_id}->{target_id}:{relationship}"
        self.edges.append({
            "id": edge_id,
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            "weight": weight
        })

    def export_analysis_graph(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a complete Graphify topology from a SatQuery analysis result dict.
        """
        # 1. Root Query Node
        q_id = self.add_node(
            node_id=f"query:{self.query_id}",
            label=f"Query: {self.query_text[:40]}...",
            node_type="QUERY",
            metadata={"full_text": self.query_text, "query_id": self.query_id}
        )

        # Extract structured query details if present
        structured_query = analysis_result.get("structured_query", {})
        location_name = structured_query.get("location_name") or analysis_result.get("location_name", "ROI Geometry")
        bbox = structured_query.get("bbox") or analysis_result.get("bbox", [])

        # 2. Location Node
        loc_id = self.add_node(
            node_id=f"loc:{location_name.lower().replace(' ', '_')}",
            label=f"Location: {location_name}",
            node_type="LOCATION",
            metadata={"bbox": bbox, "location_name": location_name}
        )
        self.add_edge(q_id, loc_id, "LOCATED_AT", weight=1.0)

        # 3. Satellite Tile Nodes & Spectral Metrics
        tiles = analysis_result.get("tiles", []) or analysis_result.get("candidate_tiles", [])
        if not tiles and "tile_id" in analysis_result:
            tiles = [analysis_result]

        for i, tile in enumerate(tiles):
            t_id_str = tile.get("tile_id", f"tile-{i+1}")
            sensor = tile.get("sensor", tile.get("provider", "Sentinel-2"))
            acq_date = tile.get("acquisition_time", tile.get("date", "2024-01-01"))
            cloud_pct = tile.get("cloud_cover", 0.0)

            t_node_id = self.add_node(
                node_id=f"tile:{t_id_str}",
                label=f"Tile: {t_id_str} ({sensor})",
                node_type="TILE",
                metadata={
                    "tile_id": t_id_str,
                    "sensor": sensor,
                    "acquisition_time": acq_date,
                    "cloud_cover": cloud_pct
                }
            )
            self.add_edge(loc_id, t_node_id, "CONTAINS_TILE", weight=0.9)

            # Spectral Metrics associated with tile
            metrics = tile.get("metrics", {}) or analysis_result.get("spectral_indices", {})
            for m_name, m_val in metrics.items():
                m_node_id = self.add_node(
                    node_id=f"metric:{m_name.lower()}:{t_id_str}",
                    label=f"Index: {m_name.upper()} = {round(m_val, 4) if isinstance(m_val, float) else m_val}",
                    node_type="SPECTRAL_METRIC",
                    metadata={"index": m_name, "value": m_val, "tile_id": t_id_str}
                )
                self.add_edge(t_node_id, m_node_id, "CALCULATED_METRIC", weight=0.85)

        # 4. Evidence Nodes
        evidence_chain = analysis_result.get("evidence_chain", []) or analysis_result.get("evidence", [])
        for ev in evidence_chain:
            if isinstance(ev, str):
                ev_obj = {"evidence_id": f"ev-{hash(ev) % 10000}", "description": ev}
            else:
                ev_obj = ev

            ev_id = ev_obj.get("evidence_id", f"ev-{len(self.nodes)}")
            desc = ev_obj.get("description", ev_obj.get("summary", "Evidence Item"))
            
            ev_node_id = self.add_node(
                node_id=f"evidence:{ev_id}",
                label=f"Evidence: {desc[:35]}...",
                node_type="EVIDENCE",
                metadata=ev_obj
            )
            self.add_edge(q_id, ev_node_id, "GROUNDED_IN", weight=0.95)

        # 5. Validated Claims
        claims = analysis_result.get("claims", []) or analysis_result.get("validated_claims", [])
        if not claims and "answer" in analysis_result:
            claims = [{"claim": analysis_result["answer"], "confidence": analysis_result.get("confidence", 0.9)}]

        for idx, cl in enumerate(claims):
            if isinstance(cl, str):
                cl_obj = {"claim": cl, "confidence": 0.9}
            else:
                cl_obj = cl

            text = cl_obj.get("claim", cl_obj.get("statement", "Claim"))
            cl_node_id = self.add_node(
                node_id=f"claim:{idx+1}",
                label=f"Claim #{idx+1}: {text[:35]}...",
                node_type="CLAIM",
                metadata=cl_obj
            )
            
            # Connect evidence to claim
            for ev in self.nodes:
                if ev["type"] == "EVIDENCE":
                    self.add_edge(ev["id"], cl_node_id, "SUPPORTS_CLAIM", weight=0.9)
            if not any(e["type"] == "EVIDENCE" for e in self.nodes):
                self.add_edge(q_id, cl_node_id, "ASSERTS_CLAIM", weight=0.8)

        # 6. Overall Confidence Node
        conf_score = analysis_result.get("confidence", analysis_result.get("confidence_score", 0.95))
        conf_category = "HIGH" if conf_score >= 0.85 else ("MEDIUM" if conf_score >= 0.65 else "LOW")
        
        conf_node_id = self.add_node(
            node_id="confidence:overall",
            label=f"Confidence: {conf_category} ({round(conf_score * 100, 1)}%)",
            node_type="CONFIDENCE",
            metadata={"score": conf_score, "category": conf_category}
        )
        
        for n in self.nodes:
            if n["type"] == "CLAIM":
                self.add_edge(n["id"], conf_node_id, "SCORED_WITH", weight=1.0)

        # Compute graph stats
        num_nodes = len(self.nodes)
        num_edges = len(self.edges)
        max_edges = num_nodes * (num_nodes - 1) if num_nodes > 1 else 1
        density = round(num_edges / max_edges, 4)

        return {
            "graphify_version": "0.9.58",
            "query_id": self.query_id,
            "query_text": self.query_text,
            "stats": {
                "node_count": num_nodes,
                "edge_count": num_edges,
                "density": density,
                "communities": 1
            },
            "nodes": self.nodes,
            "edges": self.edges
        }
