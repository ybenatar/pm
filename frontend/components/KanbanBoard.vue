<script setup lang="ts">
import { useBoard } from '~/composables/useBoard'
import type { Column } from '~/composables/useBoard'

const { columns, boardUpdated, fetchBoard, renameColumn, addCard, deleteCard, syncCardMove } = useBoard()

// Deep sync listener for AI actions
watch(boardUpdated, (newVal) => {
  console.log('[KanbanBoard] Signal received:', newVal)
  fetchBoard()
})

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
  flex-wrap: wrap;
  gap: 20px;
  padding: 0 28px 28px;
  overflow-y: auto;
  height: calc(100vh - 80px); /* 60px header + 20px top padding */
  align-items: flex-start;
  align-content: flex-start;
}
</style>
