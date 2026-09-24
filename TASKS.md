# Task Tracker

Phased progress tracker for the Medsee radiology reporting pipeline. Update checkboxes as work completes.

---

## Phase 0 — Scaffold

**Goal:** Agent-ready environment with health endpoint.

- [x] Project dependencies (`pyproject.toml`, uv scripts, ruff)
- [x] Directory layout (`api/`, `core/`, `models/`, `pipelines/`, `llm/`, `services/`)
- [x] Rich logging setup (`core/logging.py`)
- [x] Settings model (`core/config.py`)
- [x] FastAPI app + `GET /health`
- [x] `AGENTS.md`, `TASKS.md`, Cursor rules, hooks
- [x] Smoke test (`tests/test_health.py`)
- [x] Package renamed to `medsee` (`pyproject.toml`, `src/medsee/`, imports, tests)
- [x] Backend startup script (`scripts/start-backend.ps1`)
- [x] Legacy interview-brief references removed from docs and repo

**Done when:** `uv run pytest -q` passes, dev server serves `/health` with 200.

---

## Phase 1 — Contracts

**Goal:** Define all Pydantic request/response models before writing logic.

- [x] `UrgencyFlag` enum: CRITICAL, IMPORTANT, ROUTINE
- [x] `StepStatus` enum: success, failed, skipped
- [x] `Finding` model: location, description, severity, confidence_score
- [x] `FindingsResult` model: findings list + metadata
- [x] `ReportResult` model: impression, recommendations, urgency
- [x] `IntakeMetadata` model: modality, body_part, clinical_context
- [x] `PipelineResponse` envelope: findings, report, metadata, step_statuses, confidence

**Files:** `src/medsee/models/`

**Done when:** All models import cleanly; OpenAPI reflects schemas when wired to routes.

---

## Phase 2 — Intake

**Goal:** Accept image upload with metadata; route by modality.

- [x] `POST /reports` endpoint accepting multipart form (image + metadata JSON)
- [x] Metadata validation via Pydantic
- [x] Modality routing using `pipelines/configs/modalities.json`
- [x] Return 422 for invalid modality/metadata

**Files:** `src/medsee/api/routes/reports.py`, `src/medsee/pipelines/`, `src/medsee/services/`

**Done when:** Upload with valid MRI metadata routes to MRI pipeline config; invalid modality returns 422.

---

## Phase 3 — Call 1 (Findings Extraction)

**Goal:** First LLM call analyzes image and returns structured findings.

- [x] Pydantic AI agent in `llm/findings_agent.py`
- [x] Prompt template for image analysis
- [x] Structured output: `FindingsResult` schema
- [x] Pass image bytes + clinical context to agent

**Files:** `src/medsee/llm/findings_agent.py`

**Done when:** Agent returns validated `FindingsResult` for a test image (manual or integration test).

---

## Phase 4 — Validation Gate

**Goal:** Validate Call 1 output before feeding into Call 2.

- [x] Parse LLM response into `FindingsResult`
- [x] Handle malformed JSON / schema violations gracefully
- [x] Set step status to `failed` with error detail when validation fails
- [x] Do not pass unvalidated data to Call 2

**Files:** `src/medsee/services/validation.py`

**Done when:** Malformed Call 1 output produces `step_statuses.findings_extraction = failed` without crashing.

---

## Phase 5 — Call 2 (Report Assembly)

**Goal:** Second LLM call takes validated findings and generates report.

- [x] Pydantic AI agent in `llm/report_agent.py`
- [x] Input: validated `FindingsResult` from Call 1
- [x] Output: `ReportResult` with impression, recommendations, urgency flag
- [x] Chain is real — Call 2 input is Call 1 output, not independent

**Files:** `src/medsee/llm/report_agent.py`

**Done when:** Valid findings produce a structured report with urgency flag.

---

## Phase 6 — API Envelope

**Goal:** Unified structured response for frontend rendering.

- [x] `PipelineResponse` returned from `POST /reports`
- [x] Include: findings array, report sections, metadata, confidence indicators
- [x] Include: per-step status flags (findings_extraction, report_assembly)
- [x] Orchestrator in `services/pipeline.py` wires intake → Call 1 → validate → Call 2 → envelope

**Files:** `src/medsee/services/pipeline.py`, `src/medsee/api/routes/reports.py`

**Done when:** Full pipeline returns a single JSON object matching `PipelineResponse` schema.

---

## Phase 7 — Error Paths

**Goal:** Graceful degradation when LLM steps fail.

- [x] Call 1 failure → response with empty findings, failed step flag, partial report or skip Call 2
- [x] Call 2 failure → response with findings intact, failed report step flag
- [x] API never returns 500 for LLM junk — always structured response with status flags
- [x] Log failures at WARNING level via Rich

**Files:** `src/medsee/services/pipeline.py`

**Done when:** Simulated malformed Call 1 and Call 2 failures return usable JSON with correct flags.

---

## Phase 8 — Tests

**Goal:** Automated coverage for core paths.

- [x] Happy path: upload → full pipeline → valid `PipelineResponse`
- [x] Malformed Call 1: mocked bad LLM output → degraded response
- [x] Invalid modality: 422 response
- [x] Routing: MRI vs CT vs XRAY select correct config
- [x] Mock OpenAI/Pydantic AI in unit tests (no live API calls in CI)

**Files:** `tests/`

**Done when:** `uv run pytest` covers all above scenarios with mocked LLM.

---

## Phase 9 — Web UI

**Goal:** Browser-based image upload and report display on top of the existing API.

- [x] Scaffold `frontend/` (Vite + React + Tailwind)
- [x] Upload form: image file picker + metadata fields (modality, body part, clinical context)
- [x] Submit to `POST /reports` via `FormData` (multipart)
- [x] Display `PipelineResponse`: findings, impression, recommendations, urgency, step statuses
- [x] Add CORS middleware in backend for local dev (`localhost:5173`)
- [x] Document dual-process dev workflow: `.\scripts\start-backend.ps1` + `.\scripts\start-frontend.ps1`

**Files:** `frontend/`, `src/medsee/main.py` (CORS), `README.md`

**Done when:** User can upload a sample image from the browser and see the structured report without curl.
