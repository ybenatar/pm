<script setup lang="ts">
import { useBoard } from '~/composables/useBoard'
import type { Column } from '~/composables/useBoard'

const { columns, renameColumn, addCard, deleteCard, syncCardMove } = useBoard()

/**
 * vue-draggable-plus mutates the cards array directly when dragging between columns.
 * We receive the new cards list for a column and sync it back into the composable.
 */
function onCardsChanged(columnId: string, newCards: Column['cards']) {
  const col = columns.value.find(c => c.id === columnId)
  if (col) col.cards = newCards
}
</script>

<template>
  <div class="board">
    <KanbanColumn
      v-for="col in columns"
      :key="col.id"
      :column="col"
      @rename="renameColumn"
      @addCard="addCard"
      @deleteCard="deleteCard"
      @cardsChanged="onCardsChanged"
      @syncCardMove="syncCardMove"
    />
  </div>
</template>

<style scoped>
.board {
  display: flex;
  gap: 16px;
  padding: 0 24px 24px;
  overflow-x: auto;
  flex: 1;
  align-items: flex-start;
}
</style>
