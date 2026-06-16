# Modal Backend MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable FastAPI backend without changing any existing behavior.

**Architecture:** Add a small backend under `apps/modal-backend` with focused modules for configuration, security, API routes, and map overlay work. Keep the historical import path `providers.map_overlay` intact so existing callers and tests continue to work.

**Tech Stack:** Python 3.12, FastAPI, Pillow, httpx, pytest.

---

### Task 1: Safety Baseline

**Files:**
- Create: `apps/modal-backend/tests/conftest.py`
- Create: `apps/modal-backend/tests/test_security.py`
- Create: `apps/modal-backend/security.py`

- [ ] **Step 1: Write failing tests**

Add tests for request body limiting and per-key rate limiting.

- [ ] **Step 2: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_security.py -v`

Expected: imports fail because `security.py` does not exist yet.

- [ ] **Step 3: Implement security utilities**

Add an in-memory fixed-window rate limiter and ASGI request-size middleware.

- [ ] **Step 4: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_security.py -v`

Expected: all tests pass.

### Task 2: Map Overlay Provider

**Files:**
- Create: `apps/modal-backend/providers/__init__.py`
- Create: `apps/modal-backend/providers/map_overlay.py`
- Create: `apps/modal-backend/tests/test_map_overlay.py`

- [ ] **Step 1: Write failing tests**

Add tests for parsing Nominatim results and drawing a visible map inset on an uploaded image.

- [ ] **Step 2: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_map_overlay.py -v`

Expected: imports fail because `providers.map_overlay` does not exist yet.

- [ ] **Step 3: Implement provider**

Add a `MapReference` dataclass, `parse_nominatim_place`, a cached `NominatimClient`, and `overlay_map_reference`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_map_overlay.py -v`

Expected: all tests pass.

### Task 3: API App

**Files:**
- Create: `apps/modal-backend/config.py`
- Create: `apps/modal-backend/main.py`
- Create: `apps/modal-backend/tests/test_api.py`

- [ ] **Step 1: Write failing tests**

Add tests for `/health`, invalid file rejection, oversized upload rejection, and successful overlay generation with a stubbed geocoder.

- [ ] **Step 2: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_api.py -v`

Expected: imports fail because `main.py` and `config.py` do not exist yet.

- [ ] **Step 3: Implement API**

Add `create_app`, CORS, rate limiting, upload validation, and `/v1/overlay/map`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest apps/modal-backend/tests/test_api.py -v`

Expected: all tests pass.

### Task 4: Deployability

**Files:**
- Create: `.gitignore`
- Create: `apps/modal-backend/.env.example`
- Create: `apps/modal-backend/README.md`
- Create: `apps/modal-backend/pyproject.toml`

- [ ] **Step 1: Add deployment docs and dependency metadata**

Document local run, production env vars, GitHub safety, and deployment notes.

- [ ] **Step 2: Verify**

Run: `python -m pytest apps/modal-backend/tests -v`

Expected: all tests pass.
