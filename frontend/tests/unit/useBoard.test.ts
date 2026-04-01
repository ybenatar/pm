import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'

// Mock Nuxt's useState as a plain ref
vi.stubGlobal('useState', <T>(_key: string, init: () => T) => ref(init()))

import { useBoard } from '../../composables/useBoard'

const mockColumn = (id: string, name: string, cards: any[] = []) => ({
  id, board_id: 'board1', name, order: 0, cards
})
const mockCard = (id: string, colId: string, title = 'Task', details = '') => ({
  id, column_id: colId, title, details, order: 0
})

const makeFetch = (data: any, ok = true) =>
  vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    headers: { get: () => null },
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  })

describe('useBoard', () => {
  let board: ReturnType<typeof useBoard>

  beforeEach(() => {
    vi.restoreAllMocks()
    board = useBoard()
  })

  describe('fetchBoard', () => {
    it('loads columns from the API', async () => {
      const col = mockColumn('c1', 'To Do')
      vi.stubGlobal('fetch', makeFetch({ id: 'b1', owner_id: 'u1', columns: [col] }))
      await board.fetchBoard()
      expect(board.columns.value).toHaveLength(1)
      expect(board.columns.value[0].name).toBe('To Do')
    })

    it('sets isBoardLoading to false after fetch', async () => {
      vi.stubGlobal('fetch', makeFetch({ id: 'b1', owner_id: 'u1', columns: [] }))
      await board.fetchBoard()
      expect(board.isBoardLoading.value).toBe(false)
    })
  })

  describe('setBoard', () => {
    it('replaces columns with sorted result', () => {
      const cols = [
        mockColumn('c2', 'Done', []),
        mockColumn('c1', 'To Do', []),
      ].map((c, i) => ({ ...c, order: i }))
      board.setBoard(cols)
      expect(board.columns.value).toHaveLength(2)
    })
  })

  describe('renameColumn', () => {
    it('optimistically updates the column name', async () => {
      board.setBoard([mockColumn('c1', 'Backlog')])
      vi.stubGlobal('fetch', makeFetch({ id: 'c1', name: 'Sprint 1', board_id: 'b1', order: 0 }))
      const p = board.renameColumn('c1', 'Sprint 1')
      expect(board.columns.value[0].name).toBe('Sprint 1')
      await p
    })

    it('rolls back the name if the API call fails', async () => {
      board.setBoard([mockColumn('c1', 'Backlog')])
      vi.stubGlobal('fetch', makeFetch({}, false))
      await board.renameColumn('c1', 'Sprint 1')
      expect(board.columns.value[0].name).toBe('Backlog')
    })
  })

  describe('addCard', () => {
    it('adds the card returned by the API to the column', async () => {
      board.setBoard([mockColumn('c1', 'To Do')])
      const newCard = mockCard('card1', 'c1', 'New task', 'Details')
      vi.stubGlobal('fetch', makeFetch(newCard))
      await board.addCard('c1', 'New task', 'Details')
      expect(board.columns.value[0].cards).toHaveLength(1)
      expect(board.columns.value[0].cards[0].title).toBe('New task')
    })

    it('does nothing for an unknown column id', async () => {
      board.setBoard([mockColumn('c1', 'To Do')])
      const newCard = mockCard('card1', 'unknown', 'New task', '')
      vi.stubGlobal('fetch', makeFetch(newCard))
      await board.addCard('unknown', 'New task', '')
      expect(board.columns.value[0].cards).toHaveLength(0)
    })
  })

  describe('deleteCard', () => {
    it('optimistically removes the card', async () => {
      const card = mockCard('card1', 'c1', 'Task')
      board.setBoard([mockColumn('c1', 'To Do', [card])])
      vi.stubGlobal('fetch', makeFetch(undefined, true).mockResolvedValue({
        ok: true, status: 204,
        headers: { get: () => '0' },
        json: () => Promise.resolve(undefined),
        text: () => Promise.resolve(''),
      }))
      const p = board.deleteCard('c1', 'card1')
      expect(board.columns.value[0].cards).toHaveLength(0)
      await p
    })

    it('rolls back on API failure', async () => {
      const card = mockCard('card1', 'c1', 'Task')
      board.setBoard([mockColumn('c1', 'To Do', [card])])
      vi.stubGlobal('fetch', makeFetch({}, false))
      await board.deleteCard('c1', 'card1')
      expect(board.columns.value[0].cards).toHaveLength(1)
    })
  })

  describe('syncCardMove', () => {
    it('calls PUT /api/card/:id/move with correct payload', async () => {
      board.setBoard([mockColumn('c1', 'To Do'), mockColumn('c2', 'Done')])
      const fetchMock = makeFetch(mockCard('card1', 'c2'))
      vi.stubGlobal('fetch', fetchMock)
      await board.syncCardMove('card1', 'c2', 0)
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/card/card1/move',
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })
})
