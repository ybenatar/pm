# High level steps for project

## Part 1: Plan
- [x] Read through the existing structure in `frontend/` (Nuxt 4, Playwright, Vitest).
- [x] Create `frontend/AGENTS.md` explicitly mapping out the existing code (e.g., `useBoard.ts`, `KanbanBoard.vue`, `KanbanColumn.vue`, `KanbanCard.vue`) and dependencies like `vue-draggable-plus`.
- [x] Enrich the entire `docs/PLAN.md` explicitly with checklists, exhaustive testing strategies safely utilizing `uv` and persistent Docker volumes.
- [x] Seek final user approval on the plan and the generated `frontend/AGENTS.md`.
- **Tests/Success Criteria**: `frontend/AGENTS.md` is exhaustive. `docs/PLAN.md` has checkpoints for all 10 phases. The user gives sign-off via Chat.

## Part 2: Scaffolding
- [x] Initialize Python `uv` package in `backend/` and install `fastapi`, `uvicorn`.
- [x] Create `backend/main.py` with a message "hello world" `/api/hello` route.
- [x] Create `backend/main.py` with a status "ok" `/api/health` route.
- [x] Create `Dockerfile` in root. Note: The Dockerfile should build the Nuxt frontend, then copy it and the backend into a final Python image, exposing the FastAPI port.
- [x] Create `scripts/start.sh`, `scripts/start.bat`, `scripts/stop.sh`, `scripts/stop.bat` to build and run the Docker container.
- [x] Update `docker run` commands in scripts to mount a volume (`-v pm_data:/app/data`) for the persistent SQLite database.
- **Tests/Success Criteria**: Running `start.bat` (or `.sh`) builds the image and brings up the container without errors. Hitting `http://localhost:8000/api/hello` returns `200 OK` with JSON `{"status": "ok"}`.

## Part 3: Add in Frontend
- [x] Update Nuxt `nuxt.config.ts` if needed to configure for static site generation (`ssr: false`).
- [x] Add `npm run generate` step inside the Dockerfile building phase.
- [x] Update `backend/main.py` to use `StaticFiles` to mount and serve the Nuxt static build output (the `.output/public` directory) at the `/` route.
- [x] Add fallback mechanism in FastAPI to serve `/index.html` for any unmatched route (SPA routing behavior).
- **Tests/Success Criteria**: Rebuild and start the Docker container. Hitting `http://localhost:8000/` serves the UI and shows the dummy NuxtJS Kanban board UI successfully.

## Part 4: Add in a fake user sign in experience
- [x] Create an explicit `/login` page or unified login component overlay in the NuxtJS UI.
- [x] Use a simple state variable or Nuxt `useState`/`localStorage` to track logged-in status.
- [x] Hardcode the allowed credentials: user: "user", password: "password".
- [x] Add a Nuxt middleware hook to protect the `/` route, redirecting to `/login` if no user state is found.
- [x] Update the main layout sidebar to include a prominent "Logout" button when the user is authenticated.
- **Tests/Success Criteria**: Initial load of `http://localhost:8000/` automatically redirects to the login screen. Submitting the exact credentials "user" / "password" successfully routes the user to the Kanban board. Clicking Logout invalidates the local state and returns the user to the login screen.

## Part 5: Database modeling
- [x] Propose and draft an absolute, minimal schema for SQLite (e.g., specific tables for `Board`, `Columns`, `Cards`, and maybe user-specific config if needed in the future).
- [x] Create `docs/SCHEMA.md` detailing the exact tables, columns, and relationships (storing card ordering cleanly is crucial).
- [x] Ask the user to review and sign off on `docs/SCHEMA.md` before writing DB backend logic.
- **Tests/Success Criteria**: `docs/SCHEMA.md` document exists in the project and is explicitly reviewed and approved by the user.

## Part 6: Backend
- [x] Add `sqlite3` or `SQLAlchemy` (if ORM desired) to backend dependencies. Configuration must point database creation to the mounted volume path (e.g., `data/pm.db`).
- [x] Implement backend initialization logic in FastAPI startup event to connect and ensure all tables exist (or create them).
- [x] Create fully documented REST API routes for Kanban CRUD operations:
  - `GET /api/board`
  - `POST /api/column`, `PUT /api/column/{id}`, `DELETE /api/column/{id}`
  - `POST /api/card`, `PUT /api/card/{id}`, `DELETE /api/card/{id}`
- [x] Add backend unit tests using `pytest` and `httpx` to validate logic. Aim for a sensible ~80% test coverage on critical database & route logic, focusing exclusively on valuable tests rather than empty boilerplate coverage.
- **Tests/Success Criteria**: `pytest` passes 100%. API requests independently using `curl` or Postman to endpoints return expected JSON. Database file persists after Docker container restart.

## Part 7: Frontend + Backend Integration
- [x] Strip out the hardcoded dummy data from the NuxtJS frontend.
- [x] Implement `apiFetch` wrapper using native `fetch()` in `useBoard.ts` (replacing `$fetch` for reliable SSG/CSR execution).
- [x] Upon app load (after login), `GET /api/board` should fetch the persistent board state.
- [x] Update `KanbanColumn.vue` to use SortableJS events (`@update`, `@add`) for precise drag-and-drop tracking.
- [x] Implement **Optimistic UI** updates for creating, moving, and deleting cards to ensure zero-latency UX.
- **Design Decision**: Database path set to `sqlite:////app/data/pm.db` (absolute path) to strictly align with Docker volume mount at `/app/data/`.
- **Tests/Success Criteria**: End-to-end verification. Newly created cards and moved cards persist after browser refresh (F5) and full Docker container restart.

## Part 8: AI Connectivity Scaffolding
- [ ] Add the `openai` Python SDK via `uv` to the backend.
- [ ] Create `backend/ai.py` logic configured to instantiate the client using the mapped `OPENROUTER_API_KEY` environment variable.
- [ ] Set model hardcoding explicitly to `openai/gpt-oss-120b`.
- [ ] Create a trivial testing endpoint `/api/ai/test` taking a sample "2+2" prompt.
- **Tests/Success Criteria**: Ensure the API key is passed through Docker. Making a GET request to `http://localhost:8000/api/ai/test` should return "4" reliably from OpenRouter.

## Part 9: AI Kanban Context & Structured Outputs
- [ ] Define rigorous Pydantic schemas mirroring the database layout for OpenRouter to enforce Structured Outputs for JSON completion.
- [ ] Create the primary chatting endpoint `/api/ai/chat` which accepts the user message input string.
- [ ] Implement query logic: the backend pulls the `Kanban Board` state directly from the DB, serializes it, and inserts it into a rigid global System Prompt mapping out the agent's constraints.
- [ ] Backend makes the completion request, unpacks the structured output JSON into Python objects, commits necessary model updates to SQLite, and returns both the text response + refreshed board state to the frontend.
- **Tests/Success Criteria**: Programmatically POST to `/api/ai/chat` requesting "Add a card for buying groceries to the Todo column". Expect the API to return the AI's confirmation text AND the structured DB representation indicating the new card exists. Check the actual SQLite DB to verify.

## Part 10: Beautiful Sidebar Widget Integration
- [ ] Design and build an AI Chat widget component in NuxtJS placed gracefully in the sidebar layout.
- [ ] Ensure the UI utilizes the established color palette (Accent Yellow `#ecad0a`, Blue Primary `#209dd7`, Purple Secondary `#753991`, Dark Navy `#032147`, Gray Text `#888888`).
- [ ] Wire user chat submitting to the `/api/ai/chat` route. Display loading states (spinner or typing bubbles) while the system fetches OpenRouter.
- [ ] Once the response maps back, update the Nuxt Kanban state locally using the newly returned board model structure (auto-refresh effect).
- **Tests/Success Criteria**: E2E check. In the web interface, the user types "move all cards from Doing to Done" into the beautiful chat sidebar. The AI responds reasonably, and the user directly watches the UI seamlessly animate or repopulate the cards dropping exclusively into the Done column.