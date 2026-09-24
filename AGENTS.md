# Agent Operating Manual

This document is the primary context for AI agents working on this repository.

## Project Goal

Build a **working slice** of a radiology reporting pipeline:

1. **Intake & routing** — accept an image upload with metadata (modality, body part, clinical context); route to the correct pipeline configuration by modality.
2. **Chained LLM calls** — Call 1 extracts structured findings; output is validated; Call 2 assembles a report (impression, recommendations, urgency flag).
3. **Structured API response** — return frontend-ready JSON with findings, report sections, metadata, confidence indicators, and per-step status flags.
4. **Resilience** — if Call 1 returns malformed output, the API must still return a usable response with clear failure flags (never crash).

## Architecture Map

```
src/medsee/
├── main.py              # FastAPI app factory + lifespan
├── api/                 # HTTP routes (thin — delegate to services)
├── core/                # config, logging
├── models/              # Pydantic request/response contracts
├── pipelines/           # Modality routing + pipeline configs
├── llm/                 # Pydantic AI agents (Call 1, Call 2)
└── services/            # Orchestration logic

frontend/                # (Phase 9) upload UI + report display — not yet implemented
scripts/                 # start-backend.ps1, test helpers
```

**Data flow:** Upload + metadata → modality router → Call 1 (findings) → Pydantic validation gate → Call 2 (report) → unified API envelope with step status flags.

## Web Frontend (planned — Phase 9)

The backend is API-first; a frontend fits cleanly without restructuring the repo.

**Recommended layout:** separate `frontend/` directory (Vite + React or similar) that talks to the FastAPI backend on `:8000`.

| Concern | Approach |
|---------|----------|
| Upload | HTML form → `POST /reports` multipart (`image` file + `metadata` JSON field) |
| Dev CORS | Add `CORSMiddleware` in `medsee.main` allowing `http://localhost:5173` (Vite default) |
| Prod serving | Option A: nginx serves static build, proxies `/reports` to API. Option B: mount `StaticFiles` from FastAPI for a single-process deploy |
| Report UI | Render `PipelineResponse` JSON: findings list, impression, recommendations, urgency badge, step status flags |

Do not implement Phase 9 until backend phases 0–8 remain green.

## Stack Constraints

| Concern | Choice |
|---------|--------|
| LLM provider | **OpenAI only** (via Pydantic AI) |
| Logging | **Rich** terminal logging — no Logfire, no external observability |
| Config | `pydantic-settings` + `.env` |
| Package manager | `uv` |
| Lint/format | `ruff` |

## Workflow Rules

1. **Read [`TASKS.md`](TASKS.md)** at the start of every session to see current progress.
2. **Update [`TASKS.md`](TASKS.md)** checkboxes when a phase is complete.
3. Keep changes **scoped** to the current phase — do not implement future phases early.
4. Before marking a task done, run:
   ```bash
   uv run ruff check .
   uv run pytest
   ```
5. Do not commit secrets (`.env`, API keys) — use `.env.example` for documentation.
6. Routes stay thin; business logic lives in `services/` and `llm/`.

## Implementation Order

Follow the phases in [`TASKS.md`](TASKS.md):

0. Scaffold (env, rules, hooks, health endpoint)
1. Contracts — Pydantic models, enums (urgency, step status)
2. Intake — upload endpoint, metadata validation, modality routing
3. Call 1 — findings extraction agent + structured output schema
4. Validation gate — parse/repair/reject malformed Call 1 output
5. Call 2 — report assembly agent fed by validated findings
6. API envelope — unified response with metadata, confidence, step flags
7. Error paths — degraded responses when Call 1/2 fails
8. Tests — happy path, malformed Call 1, routing cases
9. Web UI — upload form + report display (see frontend section above)

## Key Contracts

These Pydantic models live in `src/medsee/models/`:

- **IntakeMetadata** — modality, body_part, clinical_context (sent with image upload)
- **Finding** — location, description, severity, confidence_score
- **FindingsResult** — list of Finding + Call 1 metadata
- **ReportResult** — impression, recommendations, urgency (CRITICAL | IMPORTANT | ROUTINE)
- **StepStatus** — per-step status enum (success, failed, skipped)
- **PipelineResponse** — envelope: findings, report, metadata, step_statuses

## Commands Cheat Sheet

```bash
# Install/sync dependencies
uv sync

# Run dev server (hot reload)
.\scripts\start-backend.ps1
# or
uv run uvicorn medsee.main:app --reload --host 127.0.0.1 --port 8000

# Lint and format
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest -q
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (at runtime) | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o` | Vision-capable model for image analysis |
| `OPENAI_BASE_URL` | No | — | Optional proxy/compatibility endpoint |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `APP_ENV` | No | `development` | Environment name |
