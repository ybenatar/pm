import { ref } from 'vue'

export interface Card {
  id: string
  column_id: string
  title: string
  details: string
  order: number
}

export interface Column {
  id: string
  board_id: string
  name: string
  order: number
  cards: Card[]
}

const columns = ref<Column[]>([])
const isBoardLoading = ref(true)

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  // DELETE returns no body
  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return undefined as T
  }
  return res.json()
}

export function useBoard() {
  async function fetchBoard(): Promise<void> {
    try {
      isBoardLoading.value = true
      const board = await apiFetch<{ id: string; owner_id: string; columns: Column[] }>('/api/board')
      const sortedCols = board.columns.sort((a, b) => a.order - b.order)
      sortedCols.forEach(col => col.cards.sort((a, b) => a.order - b.order))
      columns.value = sortedCols
    } catch (error) {
      console.error('Failed to fetch board:', error)
    } finally {
      isBoardLoading.value = false
    }
  }

  async function renameColumn(columnId: string, name: string): Promise<void> {
    const col = columns.value.find(c => c.id === columnId)
    const oldName = col?.name
    if (col) col.name = name
    try {
      await apiFetch(`/api/column/${columnId}`, {
        method: 'PUT',
        body: JSON.stringify({ name }),
      })
    } catch (e) {
      console.error('renameColumn failed:', e)
      if (col && oldName) col.name = oldName
    }
  }

  async function addCard(columnId: string, title: string, details: string): Promise<void> {
    const col = columns.value.find(c => c.id === columnId)
    const order = col ? col.cards.length : 0
    try {
      const newCard = await apiFetch<Card>('/api/card', {
        method: 'POST',
        body: JSON.stringify({ column_id: columnId, title, details, order }),
      })
      if (col) col.cards.push(newCard)
    } catch (error) {
      console.error('addCard failed:', error)
    }
  }

  async function deleteCard(columnId: string, cardId: string): Promise<void> {
    const col = columns.value.find(c => c.id === columnId)
    const idx = col?.cards.findIndex(c => c.id === cardId) ?? -1
    const backup = idx > -1 ? col!.cards[idx] : undefined
    if (idx > -1) col!.cards.splice(idx, 1)
    try {
      await apiFetch(`/api/card/${cardId}`, { method: 'DELETE' })
    } catch (e) {
      console.error('deleteCard failed:', e)
      if (col && backup && idx > -1) col.cards.splice(idx, 0, backup)
    }
  }

  async function syncCardMove(cardId: string, toColumnId: string, toIndex: number): Promise<void> {
    try {
      await apiFetch(`/api/card/${cardId}/move`, {
        method: 'PUT',
        body: JSON.stringify({ new_column_id: toColumnId, new_order: toIndex }),
      })
    } catch (e) {
      console.error('syncCardMove failed, refetching:', e)
      await fetchBoard()
    }
  }

  return { columns, isBoardLoading, fetchBoard, renameColumn, addCard, deleteCard, syncCardMove }
}
