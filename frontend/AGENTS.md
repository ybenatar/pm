# Frontend Architecture

This document describes the state, architecture, and core dependencies of the NuxtJS frontend for the Project Management MVP.

## Tech Stack Overview

- **Framework**: [Nuxt 4](https://nuxt.com/) (configured in `nuxt.config.ts` and `package.json` for SSR/Static rendering)
- **UI Library**: Vue 3 (Composition API exclusively)
- **Drag & Drop**: `vue-draggable-plus` (handles moving cards between columns intuitively)
- **Testing**: 
    - Unit Tests: `vitest` with `@vue/test-utils` and `happy-dom`
    - End-to-End (E2E) Tests: `@playwright/test`

## Core Code Structure

### Composables
- **`composables/useBoard.ts`**: The central state management for the MVP. It defines the interfaces for `Card`, `Column`, and `Board`. Currently initialized with dummy data for immediate display. This will eventually be refactored to wrap `$fetch` calls reaching out to the FastAPI backend, utilizing `useState` or direct pinia/reactive stores to sync server state with local optimistic UI updates.

### Components
All Vue components strictly enforce Composition API standards using `<script setup>` syntax.
- **`components/KanbanBoard.vue`**: The main wrapper. Iterates over the `Board` model and renders out individual columns horizontally.
- **`components/KanbanColumn.vue`**: Represents a single phase of the Kanban board (e.g., "Backlog", "Doing"). Implements `vue-draggable-plus` logic as the drop-zone to accept dragged cards and trigger the underlying board state mutations.
- **`components/KanbanCard.vue`**: Represents the atomic unit of work. Handles click/edit states and visually represents the task titles and metadata.

## Run Commands

The `package.json` exposes the following main utilities:
- `npm run dev`: Boots the local Nuxt development server.
- `npm run build` / `npm run generate`: Assembles the static production bundle into `.output/public/`, which is designed to be served by the Python backend in the Docker scaffolding.
- `npm run test`: Fires Vitest for synchronous assertions.
- `npm run test:e2e`: Runs Chromium/Firefox integration tests via Playwright.

## Next Steps
As per Part 3 and Part 7 of `docs/PLAN.md`, this frontend simply needs to be statically generated inside the project's root Dockerfile, after which its dummy `useBoard` composable will be wired to the persistent SQLite Database through robust REST `fetch` endpoints.
