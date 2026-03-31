# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Project Management MVP: NuxtJS frontend + Python FastAPI backend, packaged in Docker. The FastAPI server serves the Nuxt static build at `/` and exposes REST API at `/api/`. An AI chat sidebar lets users manage Kanban cards via natural language.

## Commands

### Run (Docker — primary)
```bat
scripts\start.bat     # Windows: build image, start container at localhost:8000
scripts\start.sh      # Linux/Mac
scripts\stop.bat / stop.sh
```
Requires `.env` in project root with `OPENROUTER_API_KEY=...`.

### Backend (local dev, from `backend/`)
```bash
uv run uvicorn main:app --reload --port 8000
uv run pytest                          # all tests
uv run pytest tests/test_crud.py       # single test file
uv run pytest tests/test_crud.py::test_card_crud_workflow  # single test
```
Override DB for local dev: `DATABASE_URL=sqlite:///./data/pm.db uv run uvicorn main:app --reload`

### Frontend (local dev, from `frontend/`)
```bash
npm install --legacy-peer-deps
npm run dev        # dev server (proxying to backend manually required)
npm run generate   # static build to .output/public (what Docker uses)
npm run test       # Vitest unit tests
npx playwright test  # E2E tests
```

## Architecture

### Request flow
Browser → FastAPI (port 8000) → `/api/*` routes handled by Python; all other paths served from `frontend/.output/public` (Nuxt SSG output).

### Backend (`backend/`)
- `main.py` — FastAPI app, all route definitions, `CHAT_HISTORY` in-memory list, `clean_ai_response()` for repairing malformed JSON from the model
- `models.py` — SQLModel table models (`User`, `Board`, `Column`, `Card`) + read-only Pydantic models (`BoardRead`, `ColumnRead`, `CardRead`) + AI models (`AIChatResponse`, `KanbanAction`)
- `database.py` — engine creation; DB path from `DATABASE_URL` env var, defaults to `sqlite:////app/data/pm.db`
- `crud.py` — all DB operations; `create_default_user_and_board()` seeds on first startup
- `ai.py` — OpenRouter client (`get_client()`), system prompt builder (`get_system_prompt()`), board context minifier

### AI chat flow (`POST /api/ai/chat`)
1. Fetch current board from DB
2. Build system prompt with minified board state (column/card IDs + titles + details)
3. Prepend `CHAT_HISTORY` (last N turns, N from `AI_HISTORY_LIMIT` env var, default 10)
4. Call OpenRouter with `response_format: json_object`
5. Parse `actions[]` from response, apply each (`create`/`move`/`edit`/`delete`) to DB; log hallucinated IDs to `error.log`
6. Append exchange to `CHAT_HISTORY` with system notes for newly created card IDs
7. Return `{ text, actions, board }` with refreshed board state

### Frontend (`frontend/`)
- `composables/useBoard.ts` — single source of truth; `useState` for SSR-safe global state; all API calls via `apiFetch()`; optimistic UI on add/delete; `syncCardMove()` for drag-and-drop persistence
- `pages/index.vue` — Kanban board page (protected by auth middleware)
- `pages/login.vue` — hardcoded credentials: `user` / `password`; sets `localStorage` auth state
- `middleware/` — redirects unauthenticated users to `/login`
- `components/KanbanColumn.vue` — drag-and-drop via `vue-draggable-plus`, fires `syncCardMove` on `@add`/`@update`
- `components/AIChatSidebar.vue` — posts to `/api/ai/chat`, calls `setBoard()` on response to sync UI

### Database
SQLite, schema managed by SQLModel (`init_db()` on startup). IDs are 8-char hex strings (`uuid4().hex[:8]`), matching the Vue frontend's `uid()` helper. Tables: `user`, `board`, `column`, `card`.

### Docker
Multi-stage: Node 20 Alpine builds Nuxt → Python 3.12-slim runs FastAPI via `uv`. Volume `pm_data:/app/data` persists the SQLite file across restarts.

## Key constraints (from AGENTS.md)
- No over-engineering, no unnecessary defensive programming, no extra features
- No emojis anywhere
- Identify root cause before fixing — prove with evidence
- Color scheme: `#ecad0a` yellow, `#209dd7` blue, `#753991` purple, `#032147` navy, `#888888` gray
