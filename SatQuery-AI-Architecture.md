# SatQuery AI — Architecture & Engineering Design

*A conversational Vision-Language Assistant for satellite imagery, grounded in deterministic geospatial evidence.*

---

## 0. Design Philosophy (stated up front so every later decision can be checked against it)

- The LLM/VLM is an **interpreter and explainer**, never a **source of fact**.
- Every geographic, temporal, and spectral fact must come from **deterministic code**, not from model generation.
- "Insufficient evidence" is a valid, expected answer — not a failure state.
- Prefer 5 well-justified components over 20 impressive-looking ones.
- MVP ≠ production. We will explicitly tag every recommendation as MVP or Future.

---

## 1. Requirements Analysis

### 1.1 Functional Requirements
- Parse natural-language queries into structured intent (location, time range, phenomenon, indices, operation).
- Resolve locations to geometries (bbox/polygon) and validate against real geospatial data.
- Filter/retrieve satellite scenes and tiles by space, time, and metadata.
- Compute deterministic spectral indices (NDVI, NDWI, MNDWI, NDBI, NBR) from raw bands.
- Assess evidence sufficiency (cloud cover, valid pixels, temporal coverage) before answering.
- Generate a natural-language answer grounded strictly in retrieved evidence, with claim→evidence links.
- Compute a confidence level (HIGH/MEDIUM/LOW) from measurable signals.
- Return tiles, map, dates, indices, evidence, provenance, and confidence together — not just prose.
- Support multi-turn follow-ups that refine a previous structured query (e.g., "now just last week").

### 1.2 Non-Functional Requirements
- Correctness/groundedness > completeness. Refusing is better than guessing.
- Reasonable latency for a live demo (target: single query answered in well under ~20-30s for MVP scope).
- Reproducibility: same query + same data = same answer.
- Modularity: geospatial/spectral code must be swappable and unit-testable without touching the LLM layer.
- Observability: every query's pipeline stages should be inspectable (for both debugging and building demo trust).

### 1.3 Data Flow Requirements
Two independent pipelines that only meet at retrieval:
1. **Ingestion (offline/background):** raw satellite data → validated, indexed, queryable tiles.
2. **Query (online/request-time):** NL question → structured intent → filtered tiles → VLM reasoning → grounded answer.
Ingestion must **never** run synchronously inside a user request.

### 1.4 AI Requirements
- NL → structured intent extraction (constrained/structured output, e.g. JSON schema, function-calling style).
- Multimodal reasoning over a *small, pre-filtered* evidence set (not the full archive).
- Structured, evidence-linked output — not free-text answers.
- Graceful, explicit refusal when evidence is weak or absent.

### 1.5 Geospatial Requirements
- Geocoding (name → lat/lon/bbox), coordinate system consistency (WGS84 for storage/query, UTM for raster math), polygon/bbox intersection against scene footprints, tile-level spatial indexing.

### 1.6 Retrieval Requirements
- Combine hard spatial filters, hard temporal filters, structured metadata filters (cloud %, quality), and (optionally) semantic/embedding similarity — in that priority order. Spatial/temporal/metadata filtering must be deterministic and happen *before* any vector search, because vector similarity should never be relied on to enforce "is this even the right place/time."

### 1.7 Accuracy Requirements
- No answer without linked evidence IDs. No causal claims (e.g., "pollution caused this") unless a data source actually supports causality — otherwise the system may only state correlative, measured facts (e.g., "NDWI decreased").

### 1.8 Hallucination-Prevention Requirements
- Multiple independent layers (detailed in §9) — never rely on "the LLM was told to only use evidence" as the sole safeguard.

### 1.9 Scalability Requirements (mostly deferred, noted for the ADR)
- MVP: dozens of scenes, one region, filesystem storage, single process.
- Future: many regions, continuous ingestion, distributed storage, GPU inference fleet.

### 1.10 Cost Constraints
- MVP should run on free/low-cost tiers: open-weight VLM (self-hosted or free inference), Sentinel-2 L2A is free (Copernicus), FAISS is free/local, PostgreSQL can be local/free (or skipped entirely — see §8).

### 1.11 Prototype/Hackathon Constraints
- Limited time (hours, not weeks) → hardcode/pre-ingest a **small, curated dataset** for a real region (e.g., Kolkata + 1-2 comparison regions) rather than building a generic global ingestion system.
- Favor a demo that reliably works end-to-end over one that "could theoretically scale."

---

## 2. Three Candidate Architectures

### Architecture 1 — Simple Modular Monolith
```
┌─────────────────────────────────────────────┐
│                FastAPI App                    │
│  ┌────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ API     │→│ Query    │→│ Geospatial +    │ │
│  │ Layer   │ │ Parser   │ │ Temporal Filter │ │
│  └────────┘ └──────────┘ └────────┬────────┘ │
│                                    ▼          │
│  ┌────────────┐   ┌────────────────────────┐ │
│  │ FAISS index │←→│ Metadata (JSON/SQLite) │ │
│  └────────────┘   └────────────────────────┘ │
│                                    ▼          │
│  ┌────────────┐   ┌────────────────────────┐ │
│  │ Spectral    │   │ VLM Reasoning + Claim   │ │
│  │ calc (cache)│→│ Validation + Confidence  │ │
│  └────────────┘   └────────────────────────┘ │
└─────────────────────────────────────────────┘
```
- Ingestion is a **script**, run manually/ahead of time, that populates the same filesystem/SQLite/FAISS the API reads from.
- **Pros:** fastest to build/debug, one process to run/deploy, no message broker, easiest to demo.
- **Cons:** if ingestion is slow (band download, index computation), running it inline blocks the process; no natural place for "ingest new region live during the demo" without freezing the API.
- **Complexity:** low. **Scalability:** low. **Dev effort:** low. **Debugging:** easy (one stack trace). **Cost:** minimal.

### Architecture 2 — Modular Monolith + Background Worker
```
┌───────────────┐        ┌──────────────────┐
│   FastAPI App  │        │  Worker Process   │
│ (Query Pipeline)│       │ (Ingestion Pipeline)│
│                │        │                   │
│ Query Parser   │        │ Scene Discovery   │
│ Geo/Temporal   │        │ Download/Validate │
│ Filter         │        │ Cloud Mask        │
│ FAISS Retrieval│◄──────►│ Spectral Calc     │
│ Evidence Check │ shared │ Tiling            │
│ VLM Reasoning  │ storage│ Embedding + Index │
│ Confidence     │        │                   │
└───────────────┘        └──────────────────┘
        │                          │
        ▼                          ▼
   Metadata DB (SQLite/Postgres) + FAISS index + Tile/raster storage (filesystem)
```
- Ingestion runs as a separate process/queue (can be a simple background thread, `asyncio` task, or lightweight task queue like `arq`/`RQ` — not necessarily Celery/Kafka for a hackathon).
- **Pros:** query path stays fast and responsive even while ingestion runs; realistic "system design" story for judges; clean separation of concerns (deterministic offline processing vs. online reasoning); still one deployable unit conceptually (worker + API can even be one repo, two entry points).
- **Cons:** slightly more moving parts than Architecture 1 (need a job runner and a way to signal "ingestion done" — e.g., polling a status table).
- **Complexity:** medium. **Scalability:** medium (worker can be scaled independently later). **Dev effort:** medium. **Debugging:** two processes to reason about, but each is simple. **Cost:** minimal (still local/free tiers).

### Architecture 3 — Microservices / Distributed
```
API Gateway → [Query Service] → [Geo Service] → [Retrieval Service (FAISS/PostGIS)]
                                              → [VLM Inference Service]
Ingestion Service → Message Queue (Kafka/RabbitMQ) → [Band Processor] → [Index Calculator] → [Tiler] → [Embedder]
Object Storage (S3/MinIO) + PostGIS + Vector DB (Milvus/Pinecone) + Cache (Redis)
```
- **Pros:** true independent scaling, resilience, technically impressive on paper.
- **Cons:** massive overkill for a single-region hackathon prototype; multiple services to deploy/network/debug under time pressure; failure surface (network calls, service discovery, queue infra) dwarfs the actual research problem; most of the "impressiveness" is infra, not the grounding/hallucination-prevention work that's the actual point of this project.
- **Complexity:** high. **Scalability:** high. **Dev effort:** high. **Debugging:** hard (distributed tracing needed). **Cost:** non-trivial even at small scale (multiple managed services).

### 2.1 Comparison Table

| Criterion | Arch 1: Monolith | Arch 2: Monolith + Worker | Arch 3: Microservices |
|---|---|---|---|
| Build speed (hackathon) | Fastest | Fast | Slow |
| Query-path responsiveness | Risk if ingestion runs live | Good — isolated | Good |
| Complexity | Low | Medium | High |
| Debugging | Trivial | Easy (2 processes) | Hard |
| Scalability ceiling | Low | Medium | High |
| Demonstrates system-design maturity | Some | Yes — realistic separation of online/offline | Yes, but mostly infra theatre for this use case |
| Cost | Minimal | Minimal | Real infra cost |
| Failure isolation | None | Ingestion failure ≠ query failure | Best, but overkill here |
| Fit for "hallucination-prevention is the point" | Fine | Best fit | Distracts from it |

---

## 3. Selected Architecture — Reasoning

**Selected: Architecture 2 — Modular Monolith + Background Worker.**

Evaluating the initial assumption objectively rather than accepting it:

- Architecture 1 is tempting for raw speed, but satellite ingestion (download + raster math) is genuinely slow and bursty; if that runs inline in the request/response cycle even once during a live demo, the whole app appears frozen. That's a real risk, not a hypothetical one.
- Architecture 3 solves scaling problems this project doesn't have yet, at a cost (deployment complexity, debugging time, infra cost) this project can't afford in a hackathon window — and worse, it pulls engineering attention away from the part that actually matters here: hallucination prevention and evidence grounding.
- Architecture 2 gets the one property that actually matters (ingestion can't block or crash the live query path) with the least added complexity. It also happens to be the most *honest* representation of the real problem: ingestion is fundamentally an offline batch/streaming concern, and query-answering is fundamentally a fast, read-only concern. Modeling that as two processes sharing storage is not over-engineering — it's the natural shape of the problem.
- It also has a clean, low-risk migration path to Architecture 3 later (see ADR §16): each module in the monolith is already scoped like a future service, so splitting it out later is a refactor, not a rewrite.

**Conclusion: keep the original assumption — Monolith + Worker — but for the reasoned trade-off above, not by default.**

---

## 4. Final Architecture (Detailed)

```
                         ┌───────────────────────────┐
   User (chat UI) ─────► │        FastAPI (api/)      │
                         └─────────────┬─────────────┘
                                       ▼
                         ┌───────────────────────────┐
                         │  Query Orchestrator (core/) │
                         └─────────────┬─────────────┘
                 ┌─────────────────────┼─────────────────────┐
                 ▼                     ▼                     ▼
        ┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │ Query Parser    │  │ Geospatial Module  │  │ Session/Context   │
        │ (ai/) — LLM      │  │ (geospatial/)      │  │ (domain/session)  │
        │ intent extractor │  │ geocode + bbox      │  │ structured state  │
        └────────┬────────┘  └──────────┬─────────┘  └──────────────────┘
                 ▼                     ▼
        ┌─────────────────────────────────────────┐
        │        Validation (domain/)               │
        │  reject/clarify malformed structured query │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │   Retrieval Module (retrieval/)            │
        │  1. spatial filter (bbox ∩ tile footprint)  │
        │  2. temporal filter (acquisition date range)│
        │  3. metadata filter (cloud%, quality)       │
        │  4. (optional) FAISS semantic re-rank        │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │  Evidence Sufficiency Check (domain/)      │
        │  enough valid tiles/observations? if not → │
        │  refuse with reason, skip VLM entirely      │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │   VLM Reasoning (ai/)                      │
        │  input: query + tiles + indices + metadata  │
        │  output: structured claims + evidence_ids   │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │  Claim Validation (domain/)                 │
        │  every claim must cite real evidence_ids;   │
        │  causal language requires a causal source   │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │  Confidence Scoring (domain/) — deterministic│
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │  Response Assembly (api/) → JSON: answer,   │
        │  tiles, map data, indices, provenance, conf.│
        └─────────────────────────────────────────┘

  ─────────────────────── (separate process) ───────────────────────
        ┌─────────────────────────────────────────┐
        │   Ingestion Worker (workers/ + satellite/  │
        │   + processing/)                            │
        │  discover → download → validate → cloud    │
        │  mask → indices → tile → metadata →        │
        │  (optional) embed → write to shared storage │
        └─────────────────┬───────────────────────┘
                          ▼
        ┌─────────────────────────────────────────┐
        │  Shared Storage: filesystem tiles/rasters,  │
        │  SQLite/Postgres metadata, FAISS index (opt) │
        └─────────────────────────────────────────┘
```

---

## 5. Module Responsibility Map

```
satquery/
├── app/
│   ├── api/            # FastAPI routes, request/response schemas, response assembly
│   ├── core/            # orchestration: wires the query pipeline stages together, config, DI
│   ├── domain/           # pure business logic: validation, evidence sufficiency, claim
│   │                     #   validation, confidence scoring, session/state model
│   ├── ai/               # LLM/VLM boundary ONLY: intent extraction prompt+parsing,
│   │                     #   evidence-grounded reasoning prompt+parsing. No geo/math here.
│   ├── geospatial/        # geocoding, bbox/polygon math, coordinate transforms, intersection
│   ├── satellite/         # scene discovery + access (Sentinel-2/Copernicus client)
│   ├── processing/        # cloud masking, band prep, spectral index formulas, tiling
│   ├── retrieval/          # spatial+temporal+metadata filtering, FAISS wrapper, ranking
│   ├── storage/           # filesystem/object storage access, metadata DB access, FAISS I/O
│   ├── models/            # data model / ORM entities (see §6)
│   └── workers/           # ingestion pipeline entry point + background job runner
├── tests/
├── scripts/               # one-off: bootstrap ingestion for the demo region
├── data/                   # local tile/raster storage for the prototype
└── main.py
```

For each module — purpose / why / dependencies / determinism / testability:

**geospatial/** — Converts "Kolkata" into geometry and checks intersection with scene footprints. *Why:* prevents retrieving imagery from the wrong place — the single most important correctness guarantee in the system. *Depends on:* a geocoding source (e.g., Nominatim/OSM) + a geometry library (Shapely). *Must NOT know about:* LLM prompting, UI, VLM output format. *Deterministic.* *Test:* unit-test bbox math and intersection logic with fixed coordinates — no network calls in tests.

**satellite/** — Discovers and fetches Sentinel-2 scenes for a region/date range (Copernicus API client). *Why:* single integration point for the external data source, so the rest of the system never talks to Copernicus directly. *Deterministic (I/O).* *Test:* mock the API client; test retry/error handling paths.

**processing/** — Cloud masking, band selection/normalization, the five spectral-index formulas, tiling into fixed-size tiles. *Why:* this is the actual "source of truth" computation the whole hallucination-prevention story rests on — it must be simple, deterministic, and independently verifiable. *Deterministic, CPU-bound (NumPy/Rasterio).* *Test:* feed synthetic band arrays with known values, assert exact index outputs; test cloud-mask edge cases (all-cloud tile, no-data tile).

**retrieval/** — Applies spatial → temporal → metadata filters in that order, then (optionally) FAISS similarity re-ranking on the already-filtered candidate set. *Why:* keeps FAISS from ever being the thing that decides "is this the right place/time" — it only ever ranks among already-valid candidates. *Deterministic pre-filter + optional model-based re-rank.* *Test:* given a small fixed tile catalog, assert exact filter results for known query bboxes/date ranges.

**ai/** — The only place an LLM/VLM is called. Two responsibilities: (1) NL → structured intent (constrained JSON output, validated against a schema before use), (2) evidence-grounded reasoning over a *pre-filtered* evidence set, also constrained to structured output with `evidence_ids`. *Why isolated:* keeps every non-deterministic call in one auditable place; makes it trivial to swap models later. *Test:* golden-file tests with fixed example queries → assert the parsed structure matches expectations; test rejection of malformed model output.

**domain/** — Validation of parsed intent (does the phenomenon map to a supported index? is the time range sane?), evidence sufficiency check (cloud%, valid-pixel%, min observation count thresholds), claim validation (every claim string must reference `evidence_ids` that actually exist and actually support it — e.g. reject a causal claim not backed by a source flagged as causal), confidence scoring (weighted combination of deterministic signals, see §9). *Why centralized:* this is the actual hallucination-prevention logic; it must never live inside a prompt. *Deterministic.* *Test:* table-driven tests over synthetic evidence sets and expected confidence/refusal outcomes.

**storage/** — Thin wrapper over filesystem paths, metadata DB, and FAISS index files. *Why:* isolates the rest of the app from the specific storage tech, so SQLite→Postgres or filesystem→S3 later is a swap here only.

**workers/** — Entry point that runs the ingestion pipeline (§8) as a separate process from the API, writing to the same shared storage the query path reads from.

---

## 6. Data Model

| Entity | Purpose | Where it lives (MVP) | Where it could live (future) |
|---|---|---|---|
| SatelliteScene | One Sentinel-2 acquisition (scene-level metadata: date, footprint, cloud%) | SQLite table | PostGIS (geometry column) |
| Tile | Fixed-size crop of a scene, with its own bbox + stats | SQLite table + raster file on disk | PostGIS + object storage (S3) |
| SpectralObservation | Computed index values for a tile (NDVI/NDWI/etc + stats) | SQLite table (or columns on Tile if kept simple) | Postgres table, indexed by tile_id + date |
| Embedding | Optional vector representation of a tile (image/CLIP-style) | FAISS index file + id-mapping table | Milvus/pgvector |
| Query | A user's structured request (parsed intent) | In-memory / session table | Postgres, for analytics |
| Session | Conversation state across follow-up turns | In-memory dict (MVP) / SQLite | Redis (production, multi-instance) |
| Evidence | The specific tiles+observations used to answer a query, with provenance | Constructed at request time from Tile+SpectralObservation, not a persisted table in MVP | Could persist for audit/replay |
| Answer | Final structured response returned to the user | Not persisted in MVP (returned directly) | Persisted for eval/logging |

**Reasoning:** the MVP does **not** need PostGIS or a vector DB. A single SQLite file with a `tiles` table (columns: bbox as 4 floats + a simple bbox-overlap SQL check, or just Python-side Shapely filtering since the dataset is small) is sufficient for one demo region. FAISS is optional for MVP and only earns its place if semantic re-ranking is actually demoed — otherwise structured filtering alone is both simpler and more trustworthy (see §7.1). Do not add a vector DB, PostGIS, or Redis until the deterministic-filter approach actually hits a wall.

---

## 7. Retrieval & Embeddings — Should We Even Use FAISS/CLIP?

### 7.1 Retrieval architecture choice
- **Option A (FAISS only):** rejected — FAISS has no native concept of "acquisition date" or "polygon intersection"; you'd end up bolting metadata filtering onto vector search awkwardly, and it invites treating similarity as ground truth for factual questions, which is exactly the hallucination risk this project exists to avoid.
- **Option B (Metadata DB + FAISS):** ✅ selected for MVP-and-beyond. Deterministic filtering (space/time/quality) happens first in the metadata DB; FAISS, if used at all, only re-ranks the already-valid candidate set for "which of these tiles best matches the semantic phrasing of the query" (e.g., "turbid" vs. exact NDWI thresholds).
- **Option C (PostGIS + FAISS):** the production evolution of B — same logic, but spatial filtering happens in the database via real geometry types/indexes instead of Python-side Shapely. Not needed until scene/tile counts are large enough that in-memory filtering is slow.

### 7.2 Are embeddings actually useful here?
Be honest, don't assume CLIP "just helps":
- **Spectral indices should be structured numerical fields, not embedded.** A threshold like "NDWI dropped by 0.2" is a precise, deterministic fact — embedding it and doing nearest-neighbor search would *add* imprecision, not remove it. This is the single most important call in the whole retrieval design.
- **Image embeddings (CLIP-style)** are only genuinely useful for fuzzy, visually-described queries not captured by the structured schema (e.g., "show me imagery that looks disturbed/unusual") — a nice-to-have re-ranking signal, not a requirement for the MVP's example queries, all of which map cleanly to specific indices.
- **Text embeddings** for the query itself are unnecessary if the LLM is doing structured intent extraction directly — that's a more precise and more explainable path than embed-and-search.
- **Recommendation for MVP:** skip embeddings and FAISS entirely at first pass; ship deterministic structured filtering. Add FAISS as a stretch goal only if time remains, framed explicitly as "semantic re-ranking within an already-validated candidate set," never as a substitute for spatial/temporal correctness.

---

## 8. Ingestion Pipeline

```
Satellite Source (Copernicus/Sentinel-2 L2A)
 → Scene Discovery         [I/O]        find scenes intersecting region+date range
 → Download/Access          [I/O]        fetch required bands
 → Validation                [CPU]        check band completeness, no-data extent
 → Cloud Mask                [CPU]        mask unreliable pixels (uses scene's SCL band)
 → Band Preparation          [CPU]        align/resample bands to common resolution
 → Spectral Index Computation[CPU]       NDVI/NDWI/MNDWI/NDBI/NBR per pixel
 → Tile Generation           [CPU]        split into fixed-size tiles (e.g. 512x512)
 → Metadata Extraction       [CPU]        per-tile bbox, date, cloud%, valid-pixel%
 → Quality Metrics           [CPU]        flag low-quality tiles (high cloud/no-data)
 → (Optional) Embedding      [GPU/CPU]   only if FAISS re-ranking is in scope
 → Metadata Store write      [I/O]
 → Tile/raster Storage write [I/O]
```
Why every step exists:
- **Validation** exists because scenes can arrive with missing bands or corrupted files — catching this at ingestion prevents a query-time crash mid-demo.
- **Cloud masking** exists because a cloud-covered pixel produces a *meaningless* index value; without masking, "turbidity increased" could really mean "there was a cloud."
- **Tiling** exists (see §8.1) so retrieval and index stats operate on small, addressable, independently-cacheable units instead of whole scenes.
- **Quality metrics** exist so the evidence-sufficiency check (§9) has something concrete to check *before* the VLM ever runs.
- Embedding generation is the only optional/GPU-heavy step and is explicitly deferrable.

This entire pipeline runs in the **background worker**, asynchronous to any user request — it is I/O-heavy (download) and CPU-heavy (raster math), neither of which belongs on the request/response path.

### 8.1 Tiling decision
- **Full scenes:** rejected — a Sentinel-2 scene (~100km x 100km) is far larger than most queries need; loading/processing whole scenes at query time is wasteful and slow.
- **Fixed-size tiles (e.g. 512x512):** ✅ selected for MVP. Simple, predictable storage/indexing, cheap to precompute once, easy to reason about ("this tile" = one row in the DB with a fixed bbox).
- **Dynamic ROI processing:** the eventual production answer (crop exactly to the query's polygon at request time) — deferred because it reintroduces query-time raster processing latency, which the MVP explicitly wants to avoid by precomputing.

Index values are computed **once at ingestion**, cached in `SpectralObservation`, and never recomputed per user query — a query only *reads* precomputed stats plus, if truly needed, re-derives a simple aggregate (e.g., mean NDWI over N tiles) which is cheap.

---

## 9. Hallucination-Prevention Architecture (the core of this project)

No single layer "solves" hallucination — each layer closes off one specific failure mode:

| Layer | What it actually prevents | What it does NOT prevent |
|---|---|---|
| 1. Structured query extraction (constrained JSON) | LLM inventing free-form, unvalidatable intent | LLM still might mis-extract location/time — needs (2) |
| 2. Deterministic geospatial filtering | Wrong-location imagery being used as evidence | Doesn't stop the LLM from ignoring the evidence it's given |
| 3. Deterministic spectral calculation | Fabricated index numbers | Doesn't stop misinterpretation of correct numbers |
| 4. Metadata/quality validation | Confidently answering from cloud-covered/garbage data | Doesn't catch subtler quality issues (sensor drift, etc.) |
| 5. Evidence-only prompting | Reduces (does not eliminate) the model reaching for outside "knowledge" | Prompting alone is not a hard guarantee — needs (6)+(7) |
| 6. Structured model output (claims + evidence_ids) | Makes claims machine-checkable instead of trusting prose | Doesn't stop the model citing an evidence_id that doesn't support the claim — needs (7) |
| 7. Claim-to-evidence mapping / post-generation validation | Catches claims whose cited evidence doesn't actually contain the stated fact, and blocks unsupported causal language | Can't invent evidence the model *should* have used but didn't |
| 8. Confidence scoring from measurable signals | Prevents overconfident framing when data is marginal | Doesn't turn bad data into good data |
| 9. Evidence sufficiency check (pre-VLM) | Skips the VLM entirely when there isn't enough real evidence, avoiding manufactured answers from thin data | Requires the sufficiency thresholds themselves to be well-calibrated |
| 10. Refusal path | Gives the system a legitimate "I don't know" | Only as good as (9)'s thresholds |
| 11. Source/provenance tracking | Makes every claim auditable back to a tile+date+source | Doesn't itself catch a wrong claim, just makes it checkable |

**Explicit non-claim:** "retrieval-augmented generation eliminates hallucination" is false and is not asserted anywhere in this design. What's asserted is that *forcing every fact through deterministic code, and forcing every model claim to cite checkable evidence*, converts hallucination from "silent and undetectable" into "either prevented outright or visible to a validator." The concrete example from the brief — model says "industrial pollution caused the turbidity" when evidence only shows NDWI dropped — is exactly what layer 7 exists to catch: causal language is rejected unless a cited source is explicitly flagged as a causal-attribution source (which satellite indices alone never are).

---

## 10. Confidence Mechanism

Deterministic signals (all computed in `domain/confidence.py`, never asked of the LLM):
- Spatial match quality (does the tile fully cover the query polygon, or partially?)
- Temporal match quality (exact date match vs. nearest available within range)
- Cloud coverage % (lower is better)
- Valid-pixel % (higher is better)
- Number of independent observations in range (more is better, for change detection)
- Consistency across dates (do repeated observations agree, or is there noisy disagreement?)
- (If used) retrieval/re-rank similarity score — **only a minor factor, never the deciding one**

Model-based input: essentially none for the score itself — the VLM may report *its own* uncertainty about interpretation, but this is kept separate from and subordinate to the deterministic score. The final HIGH/MEDIUM/LOW label is produced by simple deterministic thresholding (e.g., weighted sum against fixed cutoffs) with the contributing reasons listed alongside it, so a MEDIUM/LOW result always comes with an explanation like "cloud coverage 40%, only 1 clear observation in range."

---

## 11. Provenance Flow

Every `Evidence` object attached to a claim carries: `tile_id`, `scene_id`, `acquisition_date`, `lat/lon` or bbox, the specific index value(s), `cloud_percentage`, and `source` ("Sentinel-2 L2A"). This object is constructed once at retrieval time from `Tile` + `SpectralObservation` rows, passed unchanged into the VLM prompt, referenced by `evidence_ids` in the VLM's structured output, and returned unchanged (not paraphrased) in the final API response's `evidence` array — so the same record the model reasoned over is the exact record the user sees, with nothing lost or altered in between.

---

## 12. Conversational Context / Session State

- **Conversation state (in-memory or lightweight session store):** the last structured `Query` object (location, geometry, time range, phenomenon, indices) — this is what a follow-up like "now just last week" patches, rather than forcing the LLM to reconstruct the whole query from scratch.
- **Database:** unaffected by session turns; only ingestion output lives here.
- **Cache:** optional — most valuable for repeated identical queries within a demo (cache the final assembled answer keyed by the structured query hash).
- **Request object:** carries the current turn's raw text plus a reference to the session, nothing else.

Design rule: the LLM is asked to produce a **diff/patch** against the existing structured query on follow-up turns (e.g., "same query, but time_range.start = 7 days ago"), not to regenerate the entire structured object — this shrinks the surface area for mis-extraction on follow-ups.

---

## 13. Query Pipeline — Transitions Explained

```
USER → API → Query Parser → Structured Query → Validation → Geospatial Resolution
  → Temporal Filtering → Metadata Filtering → (FAISS Retrieval, optional)
  → Evidence Collection → Evidence Sufficiency Check → VLM
  → Claim Validation → Confidence Calculation → Grounded Response → Map + Evidence + Citations
```
- **API → Query Parser:** raw text handed to the LLM under a strict schema/function-calling contract.
- **Structured Query → Validation:** domain code checks the schema is well-formed and the phenomenon maps to a supported index set; malformed output triggers a re-prompt or a clarification question, never a guess.
- **Geospatial Resolution:** the location string is geocoded and the result geometry, not the string, propagates forward.
- **Temporal/Metadata Filtering:** narrows the tile catalog to only tiles that pass all three deterministic filters.
- **Evidence Sufficiency Check:** if the filtered set is empty or below quality thresholds, the pipeline **exits here** with a refusal — the VLM is never called on insufficient data.
- **VLM:** receives only the already-validated evidence set plus the original query; nothing else.
- **Claim Validation → Confidence → Response:** as detailed in §9-§11.

---

## 14. Performance Bottlenecks & Optimization

| Bottleneck | MVP approach | Production approach |
|---|---|---|
| Downloading imagery | Pre-ingest a small fixed set before the demo | Scheduled/streaming ingestion, parallel downloads |
| Raster processing / cloud masking | Run once at ingestion, cache results | Parallelized across workers, possibly GPU-accelerated |
| Spectral index computation | Compute once, store in DB, never recompute per query | Same principle, at larger scale with batch jobs |
| Tiling | Precomputed at ingestion | Same, possibly with dynamic ROI as an added path |
| Embedding generation | Skip unless needed; if used, batch offline | GPU batch inference, vector DB with ANN indexing |
| VLM inference | Keep evidence set small (pre-filtered tiles only, not whole scenes) | Batching, model serving infra, possibly smaller distilled model |
| FAISS search | N/A for MVP (small catalog, or skip FAISS) | Quantization (IVF/PQ) at scale |
| Repeated identical queries | Simple in-memory response cache keyed by structured query | Redis cache, TTL by data freshness |

Do not optimize the parts that aren't the bottleneck — for a hackathon-scale dataset, in-memory Python filtering over a few hundred tiles is already fast enough; premature caching/indexing there wastes build time better spent on the grounding logic.

---

## 15. Failure Modes

| Failure | Graceful behavior |
|---|---|
| Satellite API unavailable | Ingestion worker retries with backoff; query path serves already-ingested data and states data may not be current |
| Imagery doesn't exist for region/date | Evidence sufficiency check fails → explicit "no imagery available for this period/region" |
| Cloud coverage too high | Same — sufficiency check fails on cloud% threshold, explicit message naming the reason |
| Geocoding fails | Ask the user to clarify/rephrase the location; never guess a geometry |
| FAISS unavailable | Skip semantic re-rank, fall back to deterministic filter order only (since FAISS is optional in this design, this is a non-event) |
| VLM fails/times out | Return the deterministic evidence (tiles, indices, provenance) without prose, with a note that reasoning failed — never fabricate the missing narrative |
| Embedding generation fails | Log and skip; tile is still usable via structured filters |
| Malformed LLM output | Reject, re-prompt once with the schema restated, then fall back to a clarification question |
| No relevant tiles found | Explicit refusal with reason (not "0 results" silently) |
| Conflicting evidence | Surface both observations and lower confidence, rather than picking one silently |
| Unsupported question type | Explicit "this system currently supports vegetation/water/urban/burn-related change queries" rather than attempting an ungrounded answer |
| Stale satellite data | Provenance always shows acquisition date, so staleness is visible to the user by design |

---

## 16. Security & Reliability (MVP-appropriate)

- Input validation on all API payloads (schema-enforced request bodies).
- File validation on any uploaded/ingested imagery (type/size checks) before passing to GDAL.
- Prompt-injection awareness: user text only ever flows into the *intent extraction* prompt, never directly into a prompt that has tool/file access or admin capability; the VLM's evidence-reasoning prompt only ever receives system-selected evidence, not arbitrary user-supplied content.
- Validate all model output against schemas before using it anywhere downstream (never `eval`/blindly trust JSON-looking text).
- Basic rate limiting on the API (even a simple in-memory limiter is enough for a hackathon demo).
- Resource limits: cap max tiles per query, max time range, to bound worst-case latency/cost.
- Secrets (Copernicus credentials, model API keys) via environment variables, never hardcoded.
- Structured logging + clear error responses (no stack traces leaked to the client).
- Full authentication/authorization is explicitly **not** needed for a hackathon demo unless multi-user persistence is in scope.

---

## 17. Observability

Track (simple structured logs/counters are enough for MVP — no need for a full metrics stack):
- End-to-end request latency, broken down by pipeline stage (parse / geo-resolve / filter / VLM / validate).
- Number of tiles retrieved per query, and how many were filtered out at each stage.
- Cloud coverage and evidence-sufficiency outcome per query (pass/refuse + reason).
- Confidence label distribution across demo queries.
- Failed queries, with the failing stage.
- Ingestion job success/failure counts and duration.
- Cache hit rate (once caching exists).

This is what makes debugging a live demo tractable, and it doubles as material for the "hallucination rate" evaluation in §18.

---

## 18. Testing Strategy

**Unit tests:** spectral formulas against hand-computed values; cloud-mask logic on synthetic masked arrays; tile generation boundaries; geospatial intersection on known bboxes; query-parser output validated against schema on a set of example prompts; confidence-score calculation on synthetic evidence sets with known expected labels.

**Integration tests:** satellite→preprocessing (feed a small real or fixture scene through the full processing pipeline, assert tile/metadata output); preprocessing→storage (assert tiles are queryable after ingestion); query→retrieval (assert a known query returns the expected tile IDs); retrieval→VLM (assert the evidence payload handed to the VLM matches the retrieval output exactly).

**End-to-end test:** run "Show water changes near Kolkata during the last 30 days" against a pre-ingested fixture dataset; assert the response's region matches Kolkata's bbox, dates fall in range, indices returned are NDWI/MNDWI, evidence array is non-empty and each entry's tile_id exists in the fixture DB, and the answer text doesn't contain any claim without a matching `evidence_ids` entry.

**AI evaluation (small hand-built eval set, ~10-20 query/expected-answer pairs covering the example queries plus a few "should refuse" cases):** measure retrieval accuracy (right tiles selected), geographic accuracy (right region), temporal accuracy (right date range), evidence attribution rate (% of claims with valid evidence_ids), unsupported-claim rate (claims lacking or misusing evidence — should be ~0 by construction of layer 7), and refusal correctness (does it refuse exactly when evidence is genuinely insufficient, and only then).

---

## 19. MVP Implementation Plan

| Stage | Build | Input → Output | Definition of Done |
|---|---|---|---|
| 1. Backend skeleton | FastAPI app, module folders, config | — → running `/health` endpoint | App boots, empty pipeline stubs wired |
| 2. Satellite ingestion | Copernicus client, scene discovery/download for one region | Region+date → raw scene files | Can download a real Sentinel-2 L2A scene for Kolkata |
| 3. Raster preprocessing | Cloud mask, band prep | Raw bands → cleaned aligned bands | Cloud mask visibly removes flagged pixels |
| 4. Spectral index computation | NDVI/NDWI/MNDWI formulas | Bands → index arrays | Unit tests pass on synthetic + real data |
| 5. Tile + metadata storage | Tiling, SQLite schema, filesystem layout | Scene+indices → Tile rows + raster files | Query a tile by ID and get correct bbox/date/stats |
| 6. Structured retrieval | Spatial/temporal/metadata filter functions | Structured query → candidate tile list | Known query returns known correct tiles |
| 7. NL query parser | LLM prompt + schema validation | Free text → structured query JSON | 10 example queries parse into correct schema |
| 8. VLM reasoning | Evidence-grounded prompt + structured output parsing | Query+evidence → claims+evidence_ids | Output validates against schema every time |
| 9. Evidence grounding / claim validation | Claim-to-evidence checker | Claims → validated/rejected claims | Injected bad claim (fake evidence_id) is caught |
| 10. Confidence system | Deterministic scoring function | Evidence stats → HIGH/MEDIUM/LOW + reasons | Matches expected labels on synthetic cases |
| 11. Interactive map + evidence UI | Frontend (Streamlit first) | API response → rendered map+cards | End-to-end demo query renders correctly |
| 12. Evaluation & optimization | Run eval set, fix worst failures, add caching if time allows | Eval set → pass/fail report | Eval set passes at an acceptable rate for demo |

**Foundation** (must exist before AI is introduced): geospatial module, spectral index module, tiling, metadata storage, deterministic retrieval filters — stages 1-6.
**Prototype** (smallest complete end-to-end system): stages 1-9 wired together, even with a minimal/ugly UI.
**Demo** (polish for judges): stage 11 done well, a curated set of queries known to work well, visible confidence/provenance in the UI (this *is* the differentiator vs. "just another chatbot").
**Production** (explicitly out of scope now, tracked for later): PostGIS, object storage, message-queue-based ingestion, multi-region support, real vector DB, auth, horizontal scaling of the VLM.

---

## 20. Architecture Decision Record

**Decision:** Modular Monolith + Background Worker, with a metadata-DB-first (not FAISS-first) retrieval design, and no CLIP/vector embeddings in the MVP scope.

**Context:** SatQuery AI must answer natural-language questions about satellite imagery without hallucinating geographic or spectral facts, under hackathon time constraints, with a single-region demo dataset.

**Alternatives considered:**
- *Architecture 1 (pure monolith):* rejected because slow, bursty ingestion work would risk blocking the live query path during a demo.
- *Architecture 3 (microservices):* rejected as solving scale problems this project doesn't have, at a cost (deployment/debugging complexity) it can't afford, while distracting effort from the actual differentiator (grounding/hallucination-prevention).
- *FAISS-only retrieval:* rejected because vector similarity cannot enforce hard spatial/temporal correctness and would blur the line between "similar" and "true."
- *Embedding spectral indices:* rejected because numeric thresholds are precise and deterministic; embedding them adds imprecision with no compensating benefit for this use case.

**Decision:** Modular Monolith + Worker wins on the balance of build speed, correctness guarantees, and honest representation of the online/offline split in the underlying problem, without inheriting distributed-systems overhead the project doesn't need yet.

**Consequences — gained:** fast to build and debug; ingestion failures can't take down live queries; clean, already-service-shaped module boundaries; retrieval correctness rests on deterministic code, which directly supports the hallucination-prevention goal.
**Consequences — sacrificed:** no independent horizontal scaling of ingestion vs. query serving; single point of failure if the shared storage layer goes down; FAISS/embeddings left as a stretch feature rather than a guaranteed one.

**Migration path to a distributed architecture later (without a rewrite):** because `geospatial/`, `satellite/`, `processing/`, `retrieval/`, and `ai/` are already isolated modules with narrow interfaces and no cross-module state, each can become its own service behind the same interface later — e.g. `processing/` becomes a scene-processing microservice consuming from a real queue, `retrieval/` swaps its SQLite/Shapely filtering for PostGIS queries, and a vector DB replaces the FAISS wrapper — all without touching `domain/` (the hallucination-prevention logic) or `api/` (the request contract), since those two boundaries are the ones designed to stay stable.
