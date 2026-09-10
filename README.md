# SatQuery AI — Interactive Multimodal Remote Sensing Intelligence Engine

[![CI Workflow](https://github.com/satquery-ai/satquery/actions/workflows/ci.yml/badge.svg)](https://github.com/satquery-ai/satquery/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Test Suite](https://img.shields.io/badge/tests-203%20passed-brightgreen.svg)](#automated-test-suite)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**SatQuery AI** is a conversational, evidence-grounded remote-sensing assistant. Its live VQA and change-detection endpoints search public Sentinel-2 L2A scenes through the Microsoft Planetary Computer STAC API and calculate indices from Cloud Optimized GeoTIFF raster windows.

---

## 🏛️ Core Architectural Principle

> **"The LLM/VLM is an interpreter and explainer, never the source of factual satellite observations."**

All physical calculations—including spectral indices ($\text{NDVI}, \text{NDWI}, \text{MNDWI}, \text{NDBI}, \text{NBR}$), SAR speckle filtering, radiometric calibration, co-registration alignment, and spatial surface area measurements—are calculated **deterministically** via Python geospatial engines before any VLM interpretation occurs.

```
USER QUERY
  │
  ▼
 Query Understanding & Intent Classification
  │
  ▼
 Spatial / Temporal / STAC Boundary Retrieval
  │
  ▼
 Quality & Co-Registration Sufficiency Gate (Refuses invalid/cloudy queries)
  │
  ▼
 Deterministic Specialists (Optical, SAR, Change Detection, SAM Grounding)
  │
  ▼
 Vision-Language Interpreter (LiteLLM / VLM)
  │
  ▼
 Claim Validation Engine (Blocks ungrounded causal leaps & hallucinations)
  │
  ▼
 Grounded Response & Evidence Chain
```

---

## ✨ Key Features

- **Evidence Sufficiency Gating**: Refuses queries when cloud cover exceeds threshold ($>15\%$), valid pixel ratio is insufficient ($<75\%$), or co-registration shift exceeds tolerance ($>6.0\text{px}$).
- **Multi-Modal Satellite Intelligence**: Sentinel-2 L2A optical multispectral indices and Sentinel-1 SAR backscatter analysis with Lee speckle filtering.
- **Bi-Temporal Change Detection**: Automated image coregistration, difference raster math, and change segment masking.
- **Strict Anti-Hallucination Claim Validation**: Automatically verifies VLM text assertions against spatial raster metrics; prevents unsubstantiated causal claims.
- **Comprehensive Test Suite**: 203 automated unit, integration, adversarial, failure-injection, performance, and scientific validation tests.

---

## 🚀 Quickstart Guide

### Prerequisites

- **Python**: `^3.10` or `^3.11`
- **Node.js**: `^18.0` or higher
- **npm**: `^9.0` or higher

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/satquery-ai/satquery.git
cd satquery

# Install frontend dependencies
npm install

# Set up Python virtual environment for backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to create your local `.env` configuration:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API Key for VLM calls | `your_openai_api_key_here` |
| `ALLOW_MOCK_FALLBACK` | Enable deterministic fallback when API key is unset | `True` |
| `PORT` | Backend FastAPI Port | `8000` |
| `VITE_API_BASE_URL` | Frontend API Target | `http://localhost:8000` |

### Live Data Scope

- VQA and bi-temporal change detection use real Sentinel-2 L2A imagery when the request provides an AOI/date range or names a supported location.
- The API accepts `bbox`, `start_date`, and `end_date` in `POST /api/v1/analyze`. A query containing one or two years is converted into a matching date range.
- The free public catalog has rate limits and only returns scenes that satisfy the cloud-quality threshold.
- Live segmentation supports water and vegetation through measured Sentinel-2 spectral masks. Arbitrary objects still require high-resolution imagery and a dedicated model; Sentinel-1 RTC needs the configured subscription key.

### Production Environment

Set these in Render before enabling live traffic:

- `CORS_ORIGINS=https://satquery-banana.vercel.app` (add preview domains only when needed)
- `NOMINATIM_USER_AGENT` with a real contact email for public place search
- `PLANETARY_COMPUTER_SUBSCRIPTION_KEY` to enable Sentinel-1 RTC; Sentinel-2 remains public
- a persistent disk mounted for `DB_PATH` if queued jobs and the response cache must survive Render restarts

Set `VITE_API_BASE_URL` in Vercel to the existing Render backend HTTPS URL. The UI sends explicit `bbox`, `start_date`, and `end_date` fields with each live request.

### 3. Run Locally

**Start Backend FastAPI Server:**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
*API Swagger Documentation will be available at `http://localhost:8000/docs`*

**Start Frontend Console:**
```bash
npm run dev
```
*Interactive Remote Sensing Console will open at `http://localhost:3000`*

---

## 🧪 Automated Test Suite

SatQuery AI includes **203 automated tests** covering unit behavior, integration paths, adversarial hallucination injection, failure injection, performance benchmarks, and scientific validation:

```bash
# Run complete test suite (from repository root)
pytest
```

### Test Suite Structure

| Module Path | Test Count | Description |
|---|---:|---|
| `backend/tests/scientific/` | 124 | Synthetic S2/S1 raster fixtures, spectral index bounds, SAR Lee filtering, spatial geodesy, and pipeline determinism. |
| `backend/tests/integration/` | 16 | Failure injection (database corruption, corrupted index, VLM timeouts, network errors). |
| `backend/tests/eval/` | 11 | Anti-hallucination adversarial prompts, VLM grounding verification, vector retrieval evaluation. |
| `backend/tests/unit/` | 42 | Co-registration policies, claim validation, confidence scoring, VLM zero-invocation gates, geodesy. |
| `backend/tests/benchmark/` | 5 | Memory profiling and P50/P95/P99 latency benchmarks. |
| `backend/tests/e2e/` | 5 | End-to-end FastAPI endpoint integration tests. |

---

## 📦 Deployment

### Vercel (Frontend)

The repository includes a pre-configured `vercel.json` for deployment:

1. Push your repository to GitHub.
2. Import the project in Vercel.
3. Set the root directory to `./` (or `frontend/` if deploying as subfolder).
4. Build command: `npm run build`
5. Output directory: `dist`

### Production Cloud (Backend FastAPI)

Run the backend via Uvicorn or Gunicorn with ASGI workers:

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📄 Repository Structure

```text
satquery-SIH/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
├── backend/
│   ├── app/                     # Core FastAPI application & Specialists
│   │   ├── ai/                  # VLM Provider & Router
│   │   ├── core/                # Configuration & Logging
│   │   ├── domain/              # Evidence Sufficiency, Geodesy, Claim Validation
│   │   ├── services/            # Raster Ops, Co-Registration, Vector Search
│   │   └── specialists/         # VQA, Change Detection, Grounding, Optical-SAR
│   ├── tests/                   # 203 automated tests across 6 test packages
│   ├── main.py                  # FastAPI Application Entrypoint
│   └── requirements.txt         # Python dependencies
├── src/                         # React + Vite Interactive Remote Sensing UI
├── .env.example                 # Root environment template
├── pytest.ini                   # Pytest configuration
├── vercel.json                  # Vercel deployment configuration
├── package.json                 # Node package configuration & helper scripts
└── README.md                    # System documentation
```

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).
