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

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 
      'Content-Type': 'application/json',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return undefined as T
  }
  return res.json()
}

function sortBoard(boardColumns: Column[]): Column[] {
  if (!boardColumns) return []
  try {
    const sorted = [...boardColumns].sort((a: Column, b: Column) => (a.order || 0) - (b.order || 0))
    sorted.forEach((col: Column) => {
      if (col.cards && Array.isArray(col.cards)) {
        col.cards = [...col.cards].sort((a: Card, b: Card) => (a.order || 0) - (b.order || 0))
      } else {
        col.cards = []
      }
    })
    return sorted
  } catch (err) {
    console.error('Error in sortBoard:', err)
    return boardColumns || []
  }
}

export function useBoard() {
  const columns = useState<Column[]>('board:columns', () => [])
  const isBoardLoading = useState<boolean>('board:loading', () => true)
  const boardUpdated = useState<number>('board:signal', () => 0)
  const isError = useState<boolean>('board:error', () => false)

  function triggerRefresh() {
    boardUpdated.value++
  }

  async function fetchBoard(): Promise<void> {
    try {
      isError.value = false
      // Background refresh if data already exists to avoid UI flicker/loop
      if (columns.value.length === 0) {
        isBoardLoading.value = true
      }

      const board = await apiFetch<{ id: string; owner_id: string; columns: Column[] }>('/api/board')
      if (board && board.columns) {
        columns.value = sortBoard(board.columns)
      }
    } catch (error) {
      console.error('[useBoard] Error: fetchBoard failed', error)
      isError.value = true
    } finally {
      isBoardLoading.value = false
    }
  }

  function setBoard(newColumns: Column[]): void {
    columns.value = sortBoard(newColumns)
  }

  async function renameColumn(columnId: string, name: string): Promise<void> {
    const col = columns.value.find((c: Column) => c.id === columnId)
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
    const col = columns.value.find((c: Column) => c.id === columnId)
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
    const col = columns.value.find((c: Column) => c.id === columnId)
    const idx = col?.cards.findIndex((c: Card) => c.id === cardId) ?? -1
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

  return { columns, isBoardLoading, isError, boardUpdated, fetchBoard, setBoard, triggerRefresh, renameColumn, addCard, deleteCard, syncCardMove }
}
