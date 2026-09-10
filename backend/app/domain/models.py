from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class SensorType(str, Enum):
    OPTICAL_SENTINEL2 = "Sentinel-2 MSI"
    OPTICAL_LANDSAT = "Landsat-9 OLI"
    SAR_SENTINEL1 = "Sentinel-1 SAR C-Band"
    HIGH_RES = "WorldView-3 / PlanetScope"
    UNKNOWN = "Unknown Sensor"

class TaskType(str, Enum):
    VQA = "Visual Question Answering"
    GROUNDING = "Visual Grounding & Segmentation"
    CHANGE_DETECTION = "Bi-Temporal Change Detection"
    OPTICAL_SAR_FUSION = "Optical-SAR Multimodal Fusion"
    AUTO_CLASSIFIED = "Auto-Classified Query"

class CoRegistrationQuality(BaseModel):
    shift_x_px: float = Field(default=0.0, description="Horizontal shift in pixels")
    shift_y_px: float = Field(default=0.0, description="Vertical shift in pixels")
    total_shift_px: float = Field(default=0.0, description="Total Euclidean shift in pixels")
    correlation_score: float = Field(default=0.99, description="ECC Phase Correlation score [0..1]")
    is_aligned: bool = Field(default=True, description="True if total shift <= max threshold")
    applied_warp: bool = Field(default=False, description="True if affine warp was applied to correct shift")

class ImageMetadata(BaseModel):
    id: str = Field(..., description="Unique image ID")
    sensor: SensorType = SensorType.OPTICAL_SENTINEL2
    date: str = Field(..., description="Acquisition date (YYYY-MM-DD)")
    spatial_resolution_m: float = Field(default=10.0, description="Pixel size in meters")
    cloud_cover_percent: float = Field(default=0.0, description="Percentage of cloud cover [0..100]")
    width: int = Field(default=1024)
    height: int = Field(default=1024)
    bbox: List[float] = Field(default=[-180.0, -90.0, 180.0, 90.0], description="[min_lon, min_lat, max_lon, max_lat]")
    bands_available: List[str] = Field(default_factory=lambda: ["B2", "B3", "B4", "B8"])
    collection: Optional[str] = Field(default=None, description="STAC collection identifier")
    source_uri: Optional[str] = Field(default=None, description="Canonical STAC item URL")

class ImagePairMetadata(BaseModel):
    t1: ImageMetadata
    t2: ImageMetadata
    time_gap_days: int = Field(default=0)

class SpectralIndices(BaseModel):
    ndvi_mean: Optional[float] = None
    ndvi_max: Optional[float] = None
    ndwi_mean: Optional[float] = None
    mndwi_mean: Optional[float] = None
    ndbi_mean: Optional[float] = None
    nbr_mean: Optional[float] = None

class Evidence(BaseModel):
    evidence_id: str = Field(..., description="Unique ID for citation tracking")
    evidence_type: str = Field(..., description="e.g. BandMath, CoRegistration, SpeckleFilter, SAMGrounding")
    layer: str = Field(..., description="Source band/layer used (e.g. Sentinel-2 B8/B4, Sentinel-1 VV/VH)")
    description: str = Field(..., description="Human and machine readable proof claim")
    metric_name: str = Field(..., description="Name of computed metric")
    metric_value: Union[float, str, List[float], Dict[str, float]] = Field(..., description="Quantitative value")
    unit: str = Field(default="", description="Measurement unit (e.g. %, sq_km, dB, index)")
    bbox: Optional[List[float]] = Field(default=None, description="Spatial bounding box if applicable")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ConfidenceFactors(BaseModel):
    valid_pixel_ratio: float = Field(default=1.0)
    cloud_penalty: float = Field(default=0.0)
    coregistration_penalty: float = Field(default=0.0)
    spectral_sanity_score: float = Field(default=1.0)

class Confidence(BaseModel):
    score: float = Field(..., description="Overall confidence score [0.0 to 1.0]")
    rating: str = Field(..., description="HIGH, MEDIUM, or LOW")
    factors: ConfidenceFactors

class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    crs: str = "EPSG:4326"

class GroundingMask(BaseModel):
    id: str
    label: str
    confidence: float
    bbox: List[float] = Field(..., description="[xmin, ymin, xmax, ymax]")
    polygon_geojson: Optional[Dict[str, Any]] = None
    area_sq_m: Optional[float] = None

class ChangeMapResult(BaseModel):
    changed_area_sq_km: float = Field(default=0.0)
    percent_change: float = Field(default=0.0)
    change_type: str = Field(default="Inundated / Vegetation Shift")
    confidence: float = Field(default=0.95)
    class_breakdown: Dict[str, float] = Field(default_factory=dict)
    change_polygons_count: int = Field(default=0)

class AnalysisRequest(BaseModel):
    query: str = Field(..., description="Natural language query string")
    scenario_id: Optional[str] = Field(default=None, description="Optional ID for pre-loaded SIH evaluator scenarios")
    task_type: Optional[TaskType] = Field(default=TaskType.AUTO_CLASSIFIED)
    image_url: Optional[str] = Field(default=None, description="Single raster image input URL/path")
    image_pair_urls: Optional[List[str]] = Field(default=None, description="Pair of raster image inputs for bi-temporal analysis")
    bbox: Optional[List[float]] = Field(default=None, description="Optional AOI as [min_lon, min_lat, max_lon, max_lat] in EPSG:4326")
    start_date: Optional[str] = Field(default=None, description="Inclusive ISO-8601 acquisition date/time")
    end_date: Optional[str] = Field(default=None, description="Inclusive ISO-8601 acquisition date/time")
    use_sar_despeckle: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.70)

class AnalysisResult(BaseModel):
    request_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    query: str
    task_type: TaskType
    refusal_triggered: bool = Field(default=False)
    refusal_reason: Optional[str] = None
    summary_answer: str
    evidence_chain: List[Evidence]
    confidence: Confidence
    coregistration: Optional[CoRegistrationQuality] = None
    grounding_masks: List[GroundingMask] = Field(default_factory=list)
    change_map: Optional[ChangeMapResult] = None
    spectral_indices: Optional[SpectralIndices] = None
    image_primary_url: Optional[str] = Field(default=None, description="Rendered RGB preview for the selected primary live scene")
    image_secondary_url: Optional[str] = Field(default=None, description="Rendered RGB preview for the comparison scene")
    scene_dates: List[str] = Field(default_factory=list, description="Acquisition dates used in the analysis")
    processing_time_ms: float = Field(default=0.0)
