# Fix Plan — Code Review Actions

Reference: `docs/code_review.md`

Each part is a self-contained batch of related fixes. Parts are ordered so that earlier parts do not depend on later ones. Run all tests at the end of each part before moving to the next.

---

## Part 1: Backend data correctness
**Covers:** H9, M1, M2, M3
**Files:** `backend/crud.py`, `backend/models.py`

- [x] **H9** — Fix `update_card()` to commit title/details before delegating to `move_card()`.
  - In `crud.py:update_card()`: after setting `card.title` and `card.details`, call `session.add(card)` and `session.commit()` before the move branch.
  - Remove the implicit reliance on SQLAlchemy dirty tracking across two function calls.

- [x] **M1** — Renormalize column card orders after every `move_card()`.
  - At the end of `crud.py:move_card()`, after the commit, re-query all cards in `new_column_id` ordered by `Card.order`, then re-assign `order = 0, 1, 2...` and commit.
  - This eliminates growing order gaps after multiple moves.

- [x] **M2** — Guard `create_default_user_and_board()` against race-condition duplicate inserts.
  - Import `sqlalchemy.exc.IntegrityError`.
  - Wrap the `user` insert in a try/except on `IntegrityError`; on except, re-query for the existing user and continue.
  - This prevents a silent swallow of a failed duplicate insert.

- [x] **M3** — Add cascade delete to model relationships.
  - In `models.py`, `Board.columns` relationship: add `cascade="all, delete-orphan"`.
  - In `models.py`, `Column.cards` relationship: add `cascade="all, delete-orphan"`.

**Success criteria:** `uv run pytest tests/ -v` passes all 6 tests.

---

## Part 2: AI pipeline cleanup
**Covers:** H3, H4, M4, M5, M9, M12, L1
**Files:** `backend/main.py`, `backend/ai.py`

- [x] **L1** — Move `import re` from inside `clean_ai_response()` to the top-level imports in `main.py`.

- [x] **H3** — Remove the regex repair logic from `clean_ai_response()`.
  - Delete the `re.sub(r',\s*([\]}])', r'\1', raw)` line (and remove the `import re` reference now at top).
  - Keep only: strip markdown fences, extract first `{` to last `}`. Do not attempt to repair malformed JSON.
  - The existing `json.JSONDecodeError` fallback at line 162–170 already handles parse failures gracefully — trust it.

- [x] **H4** — Report failed actions to the user.
  - After the action-processing loop, if `actions` was non-empty but `valid_actions_applied` is empty, append to `ai_data["text"]`: `" (No actions could be applied — card IDs may be stale. Try refreshing.)"`.

- [x] **M4 + M5** — Sanitize card data before injecting into the system prompt.
  - In `ai.py:minify_context()`, truncate `c.title` to 80 chars and `c.details` to 150 chars.
  - Strip any occurrence of `{BOARD_CONTEXT}` from card titles and details to prevent double-injection.

- [x] **M9** — Make the AI model overridable via environment variable.
  - Change `ai.py:13`: `MODEL = os.environ.get("AI_MODEL", "openai/gpt-oss-120b")`.

- [x] **M12** — Warn at startup if `OPENROUTER_API_KEY` is missing.
  - In `main.py:lifespan()`, add:
    ```python
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("WARNING: OPENROUTER_API_KEY not set — AI endpoints will fail")
    ```

**Success criteria:** `uv run pytest tests/ -v` passes. Manually verify that an intentionally broken JSON response from the AI (tested with a mock) returns the error fallback message, not corrupted data.

---

## Part 3: Persist chat history per-user in the database
**Covers:** H1
**Files:** `backend/models.py`, `backend/main.py`

- [x] Add a `ChatMessage` SQLModel table to `models.py`:
  ```python
  class ChatMessage(SQLModel, table=True):
      id: str = Field(default_factory=generate_uuid, primary_key=True)
      board_id: str = Field(foreign_key="board.id")
      role: str          # "user" or "assistant"
      content: str
      created_at: int    # unix timestamp, for ordering
  ```

- [x] Remove `CHAT_HISTORY = []` global from `main.py`.

- [x] In `ai_chat()`:
  - Load history from DB: `SELECT * FROM chatmessage WHERE board_id = ? ORDER BY created_at LIMIT {limit*2}`.
  - After successful completion, insert user message and assistant response as `ChatMessage` rows.
  - Derive `board_id` from `board.id` (already fetched at line 134).

- [x] Add a `GET /api/chat/history` endpoint that returns the last N messages for the board (so the frontend can restore history on page load, replacing `localStorage`).

- [x] Update `AIChatSidebar.vue` to load history from `/api/chat/history` on mount instead of from `localStorage`. Keep `localStorage` as a fallback only if the fetch fails.

- [x] Remove `saveMessages()` calls that write to `localStorage` (history is now server-side). Clear `localStorage` key `pm_ai_history` on first successful load from API.

**Success criteria:** Chat history survives a container restart. Multiple page reloads show the same history. `uv run pytest tests/ -v` passes (update `test_ai_chat.py` fixtures to account for DB-backed history).

---

## Part 4: Frontend state bugs
**Covers:** H5, H6, H7, H8, M6, M7, M8, M14
**Files:** `frontend/composables/useBoard.ts`, `frontend/components/AIChatSidebar.vue`, `frontend/components/KanbanColumn.vue`, `frontend/components/KanbanBoard.vue`, `frontend/app.vue`, `frontend/pages/index.vue`

- [x] **H5** — Fix `sortBoard()` card array mutation.
  - In `useBoard.ts:sortBoard()`, change `col.cards.sort(...)` to `col.cards = [...col.cards].sort(...)`.

- [x] **M14** — Remove duplicate board fetch on mount.
  - In `KanbanBoard.vue`, remove the `onMounted(() => fetchBoard())` call. `index.vue` already calls it.

- [x] **H6** — Remove `triggerRefresh()` after `setBoard()` in `AIChatSidebar.vue`.
  - Delete `triggerRefresh()` call at line 73. `setBoard()` is sufficient.
  - Remove `triggerRefresh` from the destructure at line 4 if no longer used.

- [x] **H7 + H8** — Cap and safely parse `localStorage` chat history (until Part 3 lands, or as fallback).
  - In `saveMessages()`: `localStorage.setItem('pm_ai_history', JSON.stringify(messages.value.slice(-100)))`.
  - In `onMounted`, wrap `JSON.parse(savedMessages)` in try/catch; on `SyntaxError`, clear the key and show the welcome message.

- [x] **M6** — Harden `onDragDrop` in `KanbanColumn.vue`.
  - Add explicit guard at top of function: `if (newIdx === undefined || newIdx === null) return`.
  - Change the parameter type from `any` to a typed interface or at least document the expected shape.

- [x] **M7** — Clear board state on logout.
  - In `app.vue` logout handler, before `navigateTo('/login')`:
    ```typescript
    columns.value = []
    isBoardLoading.value = true
    ```
  - Import `useBoard` in `app.vue` to access these refs.

- [x] **M8** — Expose error state from `fetchBoard()`.
  - Add `const isError = useState<boolean>('board:error', () => false)` to `useBoard.ts`.
  - In `fetchBoard()` catch block, set `isError.value = true`.
  - In `fetchBoard()` try block, set `isError.value = false` before the API call.
  - Export `isError` from `useBoard()`.
  - In `pages/index.vue`, show an error message when `isError.value` is true (e.g., "Could not load board. Check the server is running.").

**Success criteria:** `npm run test -- --run` passes all 10 unit tests. Manual smoke: logout clears the board, navigate back and board reloads correctly.

---

## Part 5: Test improvements
**Covers:** M10, M11, M13
**Files:** `backend/tests/test_ai_chat.py`, `backend/tests/conftest.py` (new), `frontend/tests/e2e/kanban.spec.ts`

- [x] **M10** — Extract mock OpenAI factory to a shared helper.
  - Create `backend/tests/conftest.py`.
  - Add a module-level `make_mock_openai(response_dict: dict)` function that returns a mock client with `chat.completions.create` returning a response with the given content.
  - In `test_ai_chat.py`, replace the three sets of duplicated mock class definitions with calls to `make_mock_openai()`.

- [x] **M11** — Switch hallucination test to use Python's logging capture.
  - In `backend/main.py`, change the error logger from an isolated `FileHandler` to use Python's standard logging hierarchy:
    ```python
    error_logger = logging.getLogger("ai_errors")
    # Remove FileHandler; let pytest caplog capture it
    if not any(isinstance(h, logging.FileHandler) for h in error_logger.handlers):
        fh = logging.FileHandler("error.log")
        ...
        error_logger.addHandler(fh)
    ```
    (Or: add a propagate=True flag so `caplog` can capture it.)
  - In `test_ai_hallucination_logging()`, replace the file-seek approach with `caplog`:
    ```python
    def test_ai_hallucination_logging(client, monkeypatch, caplog):
        with caplog.at_level(logging.ERROR, logger="ai_errors"):
            response = client.post(...)
        assert "Card ID 99999 does not exist" in caplog.text
    ```

- [x] **M13** — Prevent E2E test state pollution across runs.
  - Add `test.afterAll()` in `kanban.spec.ts` that uses the API to delete all cards created during the test run (track their IDs as tests create them), or reset the board to its seeded state via a dedicated test-reset endpoint.
  - Simpler alternative: add to `CLAUDE.md` and `playwright.config.ts` a comment stating that `docker volume rm pm_data && scripts/start.bat` must be run before E2E tests to reset state.

**Success criteria:** `uv run pytest tests/ -v` passes all 6 tests. `npx playwright test --reporter=list` passes all 5 E2E tests on a clean volume and on a second consecutive run without resetting the volume.

---

## Part 6: Configuration and infrastructure
**Covers:** H2, L2, L3, L4, L5, L6, L7
**Files:** `backend/main.py`, `backend/tests/test_crud.py`, `frontend/composables/useBoard.ts`, `frontend/nuxt.config.ts`, `frontend/middleware/auth.global.ts`, `Dockerfile`, `frontend/public/`

- [x] **H2** — Document the no-auth MVP limitation in code.
  - Add a block comment near the top of `backend/main.py` (below imports):
    ```python
    # AUTH NOTE: This app has no backend authentication. All endpoints operate as
    # a single hardcoded user ("user"). This is intentional for a local-only MVP.
    # Do not expose port 8000 on a network without adding proper authentication.
    ```

- [x] **L2** — Remove redundant `sys.path` hack from `test_crud.py`.
  - Delete lines 1–3 (`import sys`, `import os`, `sys.path.append(...)`). The `pythonpath = ["."]` in `pyproject.toml` handles this.

- [x] **L3** — Remove verbose debug logs from production composable.
  - In `useBoard.ts`, remove or wrap the four `console.log` calls (lines 61, 63, 81, 86) in `if (process.dev)`.

- [x] **L4** — Enable Nuxt devtools conditionally.
  - In `nuxt.config.ts`: `devtools: { enabled: process.env.NODE_ENV !== 'production' }`.

- [x] **L5** — Fix Dockerfile double `uv sync`.
  - Remove the premature `uv sync` step (lines 18–19 that run before backend files are copied).
  - Keep only the `uv sync --frozen --no-dev` that runs after `COPY backend/ .`.
  - The early `COPY backend/pyproject.toml backend/uv.lock*` for layer caching is fine; just don't run `sync` at that point.

- [x] **L6** — Document frontend auth middleware limitation.
  - Add a comment in `frontend/middleware/auth.global.ts` above the cookie check:
    ```typescript
    // This is a UI-only gate. The cookie value is not cryptographically validated.
    // Backend endpoints do not enforce auth. Local MVP only.
    ```

- [x] **L7** — Suppress favicon 404.
  - Add an empty `frontend/public/favicon.ico` file (1x1 pixel), or in `app.vue` (or `nuxt.config.ts` app.head), add:
    ```html
    <link rel="icon" href="data:,">
    ```

**Success criteria:** `uv run pytest tests/ -v` passes. `npm run test -- --run` passes. Docker image builds cleanly with `scripts/start.bat` and `curl http://localhost:8000/api/health` returns `{"status":"ok"}`. No favicon 404 in browser console.

---

## Execution order

| Part | Scope | Touches |
|------|-------|---------|
| 1 | Backend data correctness | `crud.py`, `models.py` |
| 2 | AI pipeline cleanup | `main.py`, `ai.py` |
| 3 | Chat history persistence | `models.py`, `main.py`, `AIChatSidebar.vue` |
| 4 | Frontend state bugs | `useBoard.ts`, Vue components |
| 5 | Test improvements | test files |
| 6 | Config & infrastructure | scattered small changes |

Parts 1 and 2 are independent and can be done in parallel. Part 3 depends on Part 1 (new DB table uses cascade from M3) and Part 2 (logging changes from M11 affect Part 5). Part 4 can be done after Part 3 (AIChatSidebar changes). Part 5 depends on Part 2 and Part 3. Part 6 is always last and fully independent of the others.
