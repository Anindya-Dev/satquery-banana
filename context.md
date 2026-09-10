# SatQuery AI — Comprehensive Backend Architecture & Context Documentation (`context.md`)

*Production Architecture, Component Responsibilities, Geospatial Engine, 12 Defense-in-Depth Layers, Hybrid Retrieval, Background Processing, and API Specifications.*

---

## 1. Executive Summary & Core Engineering Philosophy

**SatQuery AI** is a conversational Vision-Language Assistant for satellite imagery grounded in deterministic geospatial evidence.

The backend is built around one non-negotiable architectural axiom:

> **Core Architectural Axiom**: The LLM/VLM is an *interpreter and explainer*, **never the source of factual truth**. Every spatial coordinate, acquisition date, satellite observation, spectral index value, surface area, change percentage, evidence object, and citation originates from **100% deterministic code** (NumPy, OpenCV, Shapely, Haversine geodesy).

The system follows **Architecture Option 2 (Modular Monolith + Background Worker)**, maintaining a strict separation between online query handling, deterministic geospatial/spectral calculation, metadata storage, hybrid candidate retrieval, background task processing, and AI reasoning abstractions.

---

## 2. End-to-End System Query Flow

```
                                USER / CLIENT
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   FastAPI App   │
                            │ (backend/main)  │
                            └────────┬────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ Query Understanding │
                          │ (understanding/)    │
                          └──────────┬──────────┘
                                     │ Structured Query JSON
                                     ▼
                          ┌─────────────────────┐
                          │ Spatial Grounding   │
                          │ (geospatial/geocoder│
                          └──────────┬──────────┘
                                     │ Concrete BBox Geometry
                                     ▼
                          ┌─────────────────────┐
                          │ Candidate Retrieval │
                          │ (retrieval/filter)  │
                          └──────────┬──────────┘
                                     │ Spatial + Temporal Candidate Set
                                     ▼
                          ┌─────────────────────┐
                          │  FAISS Re-ranking   │
                          │ (retrieval/faiss)   │
                          └──────────┬──────────┘
                                     │ Re-ranked Candidate Tiles
                                     ▼
                          ┌─────────────────────┐
                          │ Evidence Sufficiency│
                          │ (domain/sufficiency)│
                          └──────────┬──────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
                 Refuse Query               Specialist Suite
            (Cloud >15% / Pixels <75%)      (app/specialists/)
                                                   │
                                                   ▼
                                         Deterministic Evidence
                                                   │
                                                   ▼
                                         AI Provider Abstraction
                                            (app/ai/llm_provider)
                                                   │
                                                   ▼
                                           Structured Claims
                                                   │
                                                   ▼
                                            Claim Validator
                                        (blocks causal leaps)
                                                   │
                                                   ▼
                                           Confidence Engine
                                                   │
                                                   ▼
                                        Grounded API Response
```

---

## 3. Directory Layout & Module Responsibilities

```
backend/
├── main.py                         # FastAPI root application & CORS middleware setup
├── requirements.txt                # Production dependencies (FastAPI, NumPy, OpenCV, Shapely, Pydantic)
├── app/
│   ├── api/                        # API Layer: REST endpoints & standardized error handlers
│   │   ├── routes.py               # Routes (/analyze, /scenarios, /health, /jobs, /jobs/{job_id})
│   │   └── errors.py               # Exception handlers converting domain errors to structured JSON
│   ├── core/                       # Core Setup: Settings, Typed Exceptions, Structured Logging
│   │   ├── config.py               # Pydantic v2 Settings & threshold parameters
│   │   ├── exceptions.py           # Typed domain exception hierarchy
│   │   └── logging.py              # Structlog JSON / console logger configuration
│   ├── domain/                     # Pure Business Logic & Domain Contracts
│   │   ├── models.py               # Pydantic schemas (Image, Tile, Query, Evidence, Confidence, Result)
│   │   ├── evidence.py             # Immutable Evidence collector & citation tracking
│   │   ├── confidence.py           # Transparent 4-factor Confidence Scorer
│   │   ├── claim_validator.py      # Claim validator & causal leap blocker
│   │   └── sufficiency.py          # Pre-VLM Evidence Sufficiency Gate
│   ├── understanding/              # Query Understanding Subsystem
│   │   └── query_parser.py         # NL → Structured Query JSON intent extractor
│   ├── geospatial/                 # Geospatial Core Engine
│   │   ├── geocoder.py             # Location resolver (name → BBox geometry)
│   │   ├── bbox.py                 # Haversine geodesy area calculation & GeoJSON conversion
│   │   ├── raster_ops.py           # Pure NumPy band math (NDVI, NDWI, MNDWI, NDBI, NBR)
│   │   ├── coregistration.py       # OpenCV Phase Correlation shift check + FFT fallback
│   │   └── sar_ops.py              # Enhanced Lee 5x5 filter & Sigma0 dB calibration
│   ├── satellite/                  # Satellite Provider Abstraction
│   │   ├── base.py                 # SatelliteProvider abstract base class
│   │   ├── mock_provider.py        # Curated SIH demo scenes & rasters provider
│   │   └── sentinel2.py            # Sentinel-2 STAC / Copernicus client
│   ├── retrieval/                  # Hybrid Candidate Retrieval Subsystem
│   │   ├── filter.py               # Spatial + Temporal + Quality metadata filter
│   │   ├── faiss_store.py          # Derived FAISS index & ID mapping manager
│   │   └── hybrid_retriever.py     # Filter → FAISS Semantic Re-rank pipeline
│   ├── ai/                         # AI Provider Abstraction
│   │   ├── base.py                 # VisionLanguageProvider abstract base class
│   │   └── llm_provider.py         # OpenAI / LiteLLM & Mock VLM providers
│   ├── specialists/                # Domain Specialists
│   │   ├── base.py                 # BaseSpecialist interface
│   │   ├── vqa.py                  # Single-Image VQA Specialist
│   │   ├── grounding.py            # SAM Visual Grounding Specialist
│   │   ├── change_detection.py     # Bi-Temporal Change Detection Specialist
│   │   └── optical_sar_fusion.py   # Optical-SAR Fusion Specialist
│   ├── orchestration/              # Workflow Orchestration
│   │   └── task_router.py          # TaskRouter executing the 12 Defense-in-Depth layers
│   ├── storage/                    # Metadata Database Storage Layer
│   │   └── metadata_db.py          # SQLite metadata database manager
│   └── workers/                    # Background Task Processing
│       └── job_queue.py            # Async JobManager for background tasks
└── tests/                          # Complete Test Suite (24/24 passed)
    ├── unit/                       # Unit tests (geodesy, raster math, sufficiency, validator)
    ├── integration/                # Integration tests (job queue, retrieval)
    ├── e2e/                        # End-to-end API tests
    └── eval/                       # AI Grounding & Refusal Benchmark suite
```

---

## 4. Deep-Dive Subsystem Reference

### 4.1 Core Configuration & Typed Exceptions (`app/core/`)

#### Configuration Parameters (`config.py`)
- `MAX_ALLOWED_CLOUD_PERCENT` = `15.0`: Maximum acceptable cloud cover percentage before triggering refusal.
- `MIN_VALID_PIXEL_RATIO` = `0.75`: Minimum required valid pixel ratio within the ROI ($\ge 75\%$).
- `MAX_COREGISTRATION_SHIFT_PX` = `3.0`: Maximum allowed spatial shift in pixels between bi-temporal scenes.
- `MIN_CONFIDENCE_THRESHOLD` = `0.70`: Minimum confidence threshold required for high-confidence claim assertion.
- `ALLOW_MOCK_FALLBACK` = `True`: Enables deterministic offline evaluation mode when no external LLM key is configured.

#### Typed Exception Hierarchy (`exceptions.py`)
All domain errors subclass `SatQueryException` (with HTTP status codes and machine-readable error codes):
- `QueryParsingError` (`400 QUERY_PARSING_ERROR`)
- `InvalidGeometryError` (`400 INVALID_GEOMETRY`)
- `SatelliteDataUnavailableError` (`404 SATELLITE_DATA_UNAVAILABLE`)
- `InsufficientEvidenceError` (`422 INSUFFICIENT_EVIDENCE`)
- `ClaimValidationError` (`422 CLAIM_VALIDATION_ERROR`)
- `StorageError` (`500 STORAGE_ERROR`)
- `RetrievalError` (`500 RETRIEVAL_ERROR`)
- `ModelError` (`502 MODEL_ERROR`)

---

### 4.2 Storage & Metadata Database (`app/storage/metadata_db.py`)

Thread-safe SQLite metadata storage managing tables for:
- `scenes`: `scene_id`, `provider`, `sensor`, `acquisition_time`, `bbox_json`, `cloud_cover`, `bands_json`, `source_uri`
- `tiles`: `tile_id`, `scene_id`, `bbox_json`, `cloud_cover`, `valid_pixel_ratio`, `stats_json`, `embedding_id`
- `observations`: `observation_id`, `tile_id`, `metric`, `value`, `formula`, `timestamp`
- `jobs`: `job_id`, `task_type`, `status`, `progress_pct`, `result_json`, `error_msg`, `created_at`, `updated_at`
- `sessions`: `session_id`, `history_json`, `last_intent_json`, `updated_at`

---

### 4.3 Geospatial & Geodesy Core Engine (`app/geospatial/`)

#### 1. Geocoder (`geocoder.py`)
Resolves location strings ("Kolkata", "Bhubaneswar", "Assam", "Delhi Airport", "Western Ghats") into validated WGS84 bounding boxes `[xmin, ymin, xmax, ymax]`.

#### 2. Geodesy Area Calculation (`bbox.py`)
Computes surface areas using the **Haversine geodesic distance formula** along the central latitude and meridian, avoiding flat-earth degree scaling errors:
$$\text{Area} = \text{Haversine}(\text{lat}_{\text{mid}}, \text{lon}_{\text{min}}, \text{lat}_{\text{mid}}, \text{lon}_{\text{max}}) \times \text{Haversine}(\text{lat}_{\text{min}}, \text{lon}_{\text{min}}, \text{lat}_{\text{max}}, \text{lon}_{\text{min}})$$

#### 3. Spectral Index Formulas (`raster_ops.py`)
Executes vectorized NumPy calculations:
- **NDVI**: $(\text{NIR} - \text{Red}) / (\text{NIR} + \text{Red} + \epsilon)$
- **NDWI**: $(\text{Green} - \text{NIR}) / (\text{Green} + \text{NIR} + \epsilon)$
- **MNDWI**: $(\text{Green} - \text{SWIR}) / (\text{Green} + \text{SWIR} + \epsilon)$
- **NDBI**: $(\text{SWIR} - \text{NIR}) / (\text{SWIR} + \text{NIR} + \epsilon)$
- **NBR**: $(\text{NIR} - \text{SWIR2}) / (\text{NIR} + \text{SWIR2} + \epsilon)$

#### 4. Co-registration Alignment Check (`coregistration.py`)
Computes sub-pixel horizontal ($dx$) and vertical ($dy$) shifts via **OpenCV Phase Correlation** (`cv2.phaseCorrelate`) with a Hanning window. Falls back to a **pure NumPy FFT cross-correlation** algorithm if OpenCV is unavailable.

#### 5. SAR Speckle Filter & Calibration (`sar_ops.py`)
Applies an **Enhanced Lee 5x5 Speckle Filter** on Sentinel-1 SAR intensity and calibrates digital numbers to decibel backscatter ($\sigma^0 \text{ dB} = 10 \cdot \log_{10}(\text{DN}^2 + \epsilon)$).

---

### 4.4 Pre-VLM Evidence Sufficiency & Claim Validation (`app/domain/`)

#### Evidence Sufficiency Gate (`sufficiency.py`)
Evaluates quality factors **before calling the VLM**:
- Rejects if valid pixel ratio $< 75\%$.
- Rejects if cloud cover $> 15\%$.
- **Co-Registration 3-Tier Policy**:
  - `GOOD` ($\le 3.0\text{px}$): Full analysis.
  - `DEGRADED` ($3.0\text{px} - 6.0\text{px}$): Affine warp applied, degraded confidence rating.
  - `UNUSABLE` ($> 6.0\text{px}$): Refusal with `INSUFFICIENT_EVIDENCE`.

#### Claim Validation & Causal Leap Blocker (`claim_validator.py`)
- Verifies every generated claim references a valid `evidence_id` in the gathered evidence chain.
- **Blocks unsupported causal leaps**: Replaces unproven causal assertions (e.g. *"industrial pollution caused the NDWI decrease"*) with correlative scientific statements (*"correlated with observed spectral shift in NDWI"*).
- Detects contradictory evidence trends and flags prompt injection attempts.

---

### 4.5 Transparent Confidence Engine (`app/domain/confidence.py`)

Calculates a 4-factor deterministic score:
$$\text{Score} = \text{Clamp}_{0.05}^{0.99} \left( (\text{ValidPixelRatio} \times 0.95 - \text{CloudPenalty} - \text{CoRegPenalty}) \times \text{SpectralSanity} \right)$$

- Score $\ge 0.85 \rightarrow$ **HIGH**
- Score $0.65 - 0.84 \rightarrow$ **MEDIUM**
- Score $< 0.65 \rightarrow$ **LOW**

---

### 4.6 Hybrid Candidate Retrieval & Derived FAISS Index (`app/retrieval/`)

1. **Deterministic Filter (`filter.py`)**: Applies hard Spatial BBox intersection, Temporal date range filtering, and Quality thresholds (Cloud $\le 15\%$, Valid Pixels $\ge 75\%$). This stage is **authoritative**.
2. **FAISS Index Store (`faiss_store.py`)**: Derived, rebuildable vector index mapped via `vector_id ↔ tile_id ↔ metadata_id`. Rebuildable directly from SQLite metadata records.
3. **Hybrid Retriever (`hybrid_retriever.py`)**: Executes deterministic pre-filtering first, then applies FAISS semantic re-ranking (`SEMANTIC_RERANK_MODE = MOCKED_SEMANTIC_RERANK`).

---

### 4.7 Background Worker & Job Manager (`app/workers/job_queue.py`)

`JobManager` dispatches expensive or long-running tasks to execute asynchronously in background threads without blocking HTTP request threads. Tracks job status (`PENDING` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED` / `FAILED`) in the SQLite metadata DB.

---

## 5. The 12 Defense-in-Depth Hallucination Prevention Layers

1. **Structured Query Extraction**: Parses natural language into validated `StructuredQuery` schema.
2. **Input Validation**: Rejects malformed bounds, coordinates, or dates using typed domain exceptions.
3. **Deterministic Spatial Grounding**: Geocodes location text to concrete EPSG:4326 BBoxes.
4. **Deterministic Temporal Filtering**: Filters candidates by exact date boundaries.
5. **Metadata & Quality Filtering**: Filters out tiles with high cloud cover ($>15\%$) or low valid pixels ($<75\%$).
6. **Deterministic Spectral Computation**: Calculates `NDVI`, `NDWI`, `NDBI` via pure NumPy array math.
7. **Pre-VLM Evidence Sufficiency Gate**: Skips VLM entirely if evidence is insufficient, returning a clean refusal (VLM invocation count = 0).
8. **Evidence-Only Prompting**: Passes only pre-filtered evidence objects to the VLM prompt.
9. **Structured VLM Output**: Constrains model output to JSON claims referencing `evidence_ids`.
10. **Claim-to-Evidence Validation**: Verifies cited evidence IDs exist and **blocks unsupported causal leaps**.
11. **Deterministic Confidence Calculation**: Scores output using measurable signal factors.
12. **Grounded API Response Sanitization**: Assembles structured response with full evidence provenance chain.

---

## 6. REST API Specification (`backend/app/api/routes.py`)

### 1. `POST /api/v1/analyze`
Main synchronous query analysis endpoint.

### 2. `POST /api/v1/jobs`
Submits asynchronous background analysis job. Returns `job_id` immediately.

### 3. `GET /api/v1/jobs/{job_id}`
Checks status, progress percentage, and results of an asynchronous background job.

### 4. `GET /api/v1/scenarios`
Returns the 5 official SIH evaluator demo scenarios.

### 5. `GET /api/v1/health`
Returns readiness/liveness status, active specialists, and enabled refusal gate configurations.

---

## 7. Automated Test Suite Verification

Run the full test suite from repository root:
```bash
pytest
# Or explicitly:
python -m pytest
```

**Test Results (203 Passed Across 6 Suites)**:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Administrator\Desktop\satquery-SIH
configfile: pytest.ini
testpaths: backend/tests

backend\tests\benchmark\test_performance.py .....                        [  2%]
backend\tests\e2e\test_api_endpoints.py ......                           [  5%]
backend\tests\eval\test_adversarial_hallucination.py ......              [  8%]
backend\tests\eval\test_ai_grounding.py .                                [  8%]
backend\tests\eval\test_retrieval_eval.py ....                           [ 10%]
backend\tests\integration\test_failure_injection.py ...............      [ 18%]
backend\tests\integration\test_job_queue.py .                            [ 18%]
backend\tests\scientific\test_coregistration_scientific.py ............. [ 25%]
......                                                                   [ 28%]
backend\tests\scientific\test_pipeline_determinism.py .................  [ 36%]
backend\tests\scientific\test_sar_scientific_validation.py ............. [ 42%]
backend\tests\scientific\test_scenario_scorecard.py .................... [ 52%]
...........                                                              [ 58%]
backend\tests\scientific\test_spectral_index_validation.py ............. [ 64%]
..............                                                           [ 71%]
backend\tests\scientific\test_stac_boundary.py .................         [ 79%]
backend\tests\test_coregistration.py ...                                 [ 81%]
backend\tests\test_raster_ops.py ....                                    [ 83%]
backend\tests\test_task_router.py ....                                   [ 85%]
backend\tests\unit\test_change_detection_eval.py ...                     [ 86%]
backend\tests\unit\test_claim_validator.py ....                          [ 88%]
backend\tests\unit\test_confidence_engine.py ....                        [ 90%]
backend\tests\unit\test_geodesy.py ...                                   [ 92%]
backend\tests\unit\test_mock_provider_rule.py ..                         [ 93%]
backend\tests\unit\test_provenance.py .                                  [ 93%]
backend\tests\unit\test_scientific_indices.py .....                      [ 96%]
backend\tests\unit\test_sufficiency.py ...                               [ 97%]
backend\tests\unit\test_vlm_zero_invocation.py .....                     [100%]

============================= 203 passed in 4.02s =============================
```

---

## 8. Deployment & Repository Hygiene

- **`.gitignore`**: Covers Python (`.venv`, `__pycache__`, `.pytest_cache`, `*.db`), Node (`dist/`, `node_modules/`), secrets (`.env*`), logs, and IDE configs.
- **`.env.example`**: Standard environment template for server configuration, API keys, and quality thresholds.
- **`pytest.ini`**: Configures root test execution with `pythonpath = backend .`.
- **`vercel.json`**: Configures frontend SPA deployment on Vercel.
- **`.github/workflows/ci.yml`**: GitHub Actions workflow executing backend tests (203 tests) and frontend Vite compilation on every push and pull request.

