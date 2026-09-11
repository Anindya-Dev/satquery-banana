import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "SatQuery AI Backend Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Host
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Quality & Reliability Thresholds (Consistent across modules)
    MAX_ALLOWED_CLOUD_PERCENT: float = Field(default=15.0, description="Max allowed cloud cover before refusal")
    MIN_VALID_PIXEL_RATIO: float = Field(default=0.75, description="Min valid pixel ratio within ROI")
    GOOD_COREGISTRATION_SHIFT_PX: float = Field(default=3.0, description="Max allowed spatial shift for GOOD alignment (px)")
    MAX_DEGRADED_COREGISTRATION_SHIFT_PX: float = Field(default=6.0, description="Max allowed spatial shift for DEGRADED alignment (px)")
    MAX_COREGISTRATION_SHIFT_PX: float = Field(default=3.0, description="Alias for GOOD spatial shift threshold")
    MIN_CONFIDENCE_THRESHOLD: float = Field(default=0.70, description="Min confidence score for assertion")
    
    # Semantic Retrieval State Tag
    SEMANTIC_RERANK_MODE: str = "MOCKED_SEMANTIC_RERANK"

    # LLM / AI Provider
    LITELLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_API_BASE_URL: str = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    ALLOW_MOCK_FALLBACK: bool = True

    # Public Planetary Computer STAC service. Asset URLs are signed anonymously at request time.
    STAC_API_URL: str = "https://planetarycomputer.microsoft.com/api/stac/v1"
    STAC_COLLECTION: str = "sentinel-2-l2a"
    STAC_SEARCH_LIMIT: int = 20
    RASTER_MAX_DIMENSION: int = 768
    PLANETARY_COMPUTER_SUBSCRIPTION_KEY: str = ""
    CORS_ORIGINS: str = "*"
    API_RATE_LIMIT_PER_MINUTE: int = 20
    RESPONSE_CACHE_TTL_SECONDS: int = 900
    NOMINATIM_USER_AGENT: str = "SatQueryAI-Research-SIH2026/1.0 (contact: anindya.research@gmail.com)"
    NOMINATIM_MIN_INTERVAL_SECONDS: float = 1.1
    
    # Storage & Database Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    MEDIA_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "media"))
    DB_PATH: str = os.path.abspath(os.path.join(BASE_DIR, "satquery_metadata.db"))
    FAISS_INDEX_PATH: str = os.path.abspath(os.path.join(BASE_DIR, "satquery_faiss.index"))
    FAISS_MAP_PATH: str = os.path.abspath(os.path.join(BASE_DIR, "satquery_faiss_map.json"))

    model_config = SettingsConfigDict(case_sensitive=True)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def normalize_debug(cls, value):
        if isinstance(value, str) and value.strip().lower() in {"release", "prod", "production"}:
            return False
        return value

settings = Settings()

os.makedirs(settings.MEDIA_DIR, exist_ok=True)
