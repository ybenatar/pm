import { describe, it, expect, beforeEach } from 'vitest'
import { useBoard } from '../../composables/useBoard'

describe('useBoard', () => {
  let board: ReturnType<typeof useBoard>

  beforeEach(() => {
    board = useBoard()
  })

  describe('initial state', () => {
    it('has exactly 5 columns', () => {
      expect(board.columns.value).toHaveLength(5)
    })

    it('each column has an id, name, and cards array', () => {
      for (const col of board.columns.value) {
        expect(col).toHaveProperty('id')
        expect(col).toHaveProperty('name')
        expect(col).toHaveProperty('cards')
        expect(Array.isArray(col.cards)).toBe(true)
      }
    })

    it('seeds dummy cards so the board is not empty', () => {
      const total = board.columns.value.reduce((sum, col) => sum + col.cards.length, 0)
      expect(total).toBeGreaterThan(0)
    })

    it('each card has an id, title, and details', () => {
      const allCards = board.columns.value.flatMap(col => col.cards)
      for (const card of allCards) {
        expect(card).toHaveProperty('id')
        expect(card).toHaveProperty('title')
        expect(card).toHaveProperty('details')
      }
    })
  })

  describe('renameColumn', () => {
    it('updates the column name', () => {
      const col = board.columns.value[0]
      board.renameColumn(col.id, 'Renamed')
      expect(board.columns.value[0].name).toBe('Renamed')
    })

    it('does nothing for an unknown column id', () => {
      const names = board.columns.value.map(c => c.name)
      board.renameColumn('non-existent', 'X')
      expect(board.columns.value.map(c => c.name)).toEqual(names)
    })
  })

  describe('addCard', () => {
    it('adds a card to the correct column', () => {
      const col = board.columns.value[0]
      const before = col.cards.length
      board.addCard(col.id, 'New task', 'Some details')
      expect(board.columns.value[0].cards).toHaveLength(before + 1)
    })

    it('the new card has the correct title and details', () => {
      const col = board.columns.value[0]
      board.addCard(col.id, 'My task', 'My details')
      const card = board.columns.value[0].cards.at(-1)!
      expect(card.title).toBe('My task')
      expect(card.details).toBe('My details')
    })

    it('the new card has a unique id', () => {
      const col = board.columns.value[0]
      board.addCard(col.id, 'A', '')
      board.addCard(col.id, 'B', '')
      const cards = board.columns.value[0].cards
      const ids = cards.map(c => c.id)
      expect(new Set(ids).size).toBe(ids.length)
    })

    it('does nothing for an unknown column id', () => {
      const totalBefore = board.columns.value.reduce((s, c) => s + c.cards.length, 0)
      board.addCard('non-existent', 'X', 'Y')
      const totalAfter = board.columns.value.reduce((s, c) => s + c.cards.length, 0)
      expect(totalAfter).toBe(totalBefore)
    })
  })

  describe('deleteCard', () => {
    it('removes the card from its column', () => {
      const col = board.columns.value[0]
      const card = col.cards[0]
      board.deleteCard(col.id, card.id)
      expect(board.columns.value[0].cards.find(c => c.id === card.id)).toBeUndefined()
    })

    it('does nothing for an unknown card id', () => {
      const before = board.columns.value[0].cards.length
      board.deleteCard(board.columns.value[0].id, 'ghost-card')
      expect(board.columns.value[0].cards).toHaveLength(before)
    })
  })

  describe('moveCard', () => {
    it('moves a card from one column to another', () => {
      const fromCol = board.columns.value[0]
      const toCol = board.columns.value[1]
      // Ensure source has a card
      board.addCard(fromCol.id, 'Move me', '')
      const card = board.columns.value[0].cards.at(-1)!

      board.moveCard(card.id, fromCol.id, toCol.id, 0)

      expect(board.columns.value[0].cards.find(c => c.id === card.id)).toBeUndefined()
      expect(board.columns.value[1].cards.find(c => c.id === card.id)).toBeDefined()
    })

    it('inserts the card at the correct index', () => {
      const fromCol = board.columns.value[0]
      const toCol = board.columns.value[2]
      board.addCard(fromCol.id, 'Indexed', '')
      const card = board.columns.value[0].cards.at(-1)!

      board.moveCard(card.id, fromCol.id, toCol.id, 0)

      expect(board.columns.value[2].cards[0].id).toBe(card.id)
    })
  })
})
