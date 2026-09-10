import uuid
from typing import List, Union, Dict, Any, Optional
from backend.app.domain.models import Evidence

class EvidenceCollector:
    def __init__(self):
        self._evidence_list: List[Evidence] = []

    def add(
        self,
        evidence_type: str,
        layer: str,
        description: str,
        metric_name: str,
        metric_value: Union[float, str, List[float], Dict[str, float]],
        unit: str = "",
        bbox: Optional[List[float]] = None
    ) -> Evidence:
        ev_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
        item = Evidence(
            evidence_id=ev_id,
            evidence_type=evidence_type,
            layer=layer,
            description=description,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            bbox=bbox
        )
        self._evidence_list.append(item)
        return item

    def get_all(self) -> List[Evidence]:
        return list(self._evidence_list)

    def clear(self):
        self._evidence_list.clear()
