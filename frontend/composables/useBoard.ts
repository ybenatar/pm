import { ref } from 'vue'

export interface Card {
  id: string
  title: string
  details: string
}

export interface Column {
  id: string
  name: string
  cards: Card[]
}

function uid(): string {
  return Math.random().toString(36).slice(2, 10)
}

const INITIAL_COLUMNS: Column[] = [
  {
    id: uid(),
    name: 'Backlog',
    cards: [
      { id: uid(), title: 'Design system tokens', details: 'Define color palette, spacing, and typography variables.' },
      { id: uid(), title: 'Set up CI pipeline', details: 'Configure GitHub Actions to run unit and E2E tests on every PR.' },
      { id: uid(), title: 'Write API spec', details: 'Draft OpenAPI 3.0 specification for the user management endpoints.' },
    ],
  },
  {
    id: uid(),
    name: 'To Do',
    cards: [
      { id: uid(), title: 'Build login page', details: 'Email + password login with form validation and error handling.' },
      { id: uid(), title: 'Integrate auth tokens', details: 'Store JWT in httpOnly cookie and refresh on expiry.' },
    ],
  },
  {
    id: uid(),
    name: 'In Progress',
    cards: [
      { id: uid(), title: 'Kanban drag-and-drop', details: 'Implement card drag between columns using vue-draggable-plus.' },
      { id: uid(), title: 'Responsive layout', details: 'Ensure the board is usable on tablet-width viewports.' },
    ],
  },
  {
    id: uid(),
    name: 'In Review',
    cards: [
      { id: uid(), title: 'Accessibility audit', details: 'Run axe-core and fix all critical WCAG AA violations.' },
    ],
  },
  {
    id: uid(),
    name: 'Done',
    cards: [
      { id: uid(), title: 'Project scaffolding', details: 'Nuxt 3 app initialised with TypeScript, Vitest, and Playwright.' },
      { id: uid(), title: 'Color scheme defined', details: 'Navy, yellow, purple, blue, and gray tokens agreed with the team.' },
    ],
  },
]

/**
 * Global board state singleton.
 * Provides reactive columns and all mutation operations.
 */
const columns = ref<Column[]>(INITIAL_COLUMNS)

export function useBoard() {
  function renameColumn(columnId: string, name: string): void {
    const col = columns.value.find(c => c.id === columnId)
    if (col) col.name = name
  }

  function addCard(columnId: string, title: string, details: string): void {
    const col = columns.value.find(c => c.id === columnId)
    if (col) col.cards.push({ id: uid(), title, details })
  }

  function deleteCard(columnId: string, cardId: string): void {
    const col = columns.value.find(c => c.id === columnId)
    if (!col) return
    col.cards = col.cards.filter(card => card.id !== cardId)
  }

  function moveCard(cardId: string, fromColumnId: string, toColumnId: string, toIndex: number): void {
    const from = columns.value.find(c => c.id === fromColumnId)
    const to = columns.value.find(c => c.id === toColumnId)
    if (!from || !to) return

    const cardIndex = from.cards.findIndex(c => c.id === cardId)
    if (cardIndex === -1) return

    const [card] = from.cards.splice(cardIndex, 1)
    to.cards.splice(toIndex, 0, card)
  }

  return { columns, renameColumn, addCard, deleteCard, moveCard }
}
