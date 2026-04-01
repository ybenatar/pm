<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import type { Column } from '~/composables/useBoard'

const props = defineProps<{
  column: Column
}>()

const emit = defineEmits<{
  rename: [columnId: string, name: string]
  addCard: [columnId: string, title: string, details: string]
  deleteCard: [columnId: string, cardId: string]
  cardsChanged: [columnId: string, cards: Column['cards']]
  syncCardMove: [cardId: string, toColumnId: string, toIndex: number]
}>()

// Rename
const editing = ref(false)
const editName = ref(props.column.name)

function startEdit() {
  editName.value = props.column.name
  editing.value = true
  nextTick(() => (document.getElementById(`col-input-${props.column.id}`) as HTMLInputElement)?.focus())
}

function commitRename() {
  const trimmed = editName.value.trim()
  if (trimmed && trimmed !== props.column.name) {
    emit('rename', props.column.id, trimmed)
  }
  editing.value = false
}

// Add card form
const showForm = ref(false)
const newTitle = ref('')
const newDetails = ref('')

function submitCard() {
  if (!newTitle.value.trim()) return
  emit('addCard', props.column.id, newTitle.value.trim(), newDetails.value.trim())
  newTitle.value = ''
  newDetails.value = ''
  showForm.value = false
}

function cancelForm() {
  newTitle.value = ''
  newDetails.value = ''
  showForm.value = false
}

// Drag-and-drop
const localCards = computed({
  get: () => props.column.cards,
  set: (val) => emit('cardsChanged', props.column.id, val),
})

function onDragDrop(event: any) {
  const newIdx = event.newIndex
  if (newIdx === undefined || newIdx === null) return
  const card = props.column.cards[newIdx]

  if (card) {
    emit('syncCardMove', card.id, props.column.id, newIdx)
  }
}
</script>

<template>
  <div class="column" :id="`column-${column.id}`">
    <!-- Column header -->
    <div class="column-header">
      <input
        v-if="editing"
        :id="`col-input-${column.id}`"
        v-model="editName"
        class="column-name-input"
        @blur="commitRename"
        @keyup.enter="commitRename"
        @keyup.escape="editing = false"
      />
      <h2 v-else class="column-name" @click="startEdit" :title="'Click to rename'">
        {{ column.name }}
      </h2>
      <span class="card-count">{{ column.cards.length }}</span>
    </div>

    <!-- Card list -->
    <VueDraggable
      v-model="localCards"
      group="kanban"
      animation="200"
      ghost-class="drag-ghost"
      chosen-class="drag-chosen"
      class="card-list"
      :id="`card-list-${column.id}`"
      @update="onDragDrop"
      @add="onDragDrop"
    >
      <KanbanCard
        v-for="card in column.cards"
        :key="card.id"
        :card="card"
        :columnId="column.id"
        @delete="(colId, cardId) => emit('deleteCard', colId, cardId)"
      />
    </VueDraggable>

    <!-- Add card -->
    <div v-if="showForm" class="add-form">
      <input
        v-model="newTitle"
        placeholder="Card title"
        :id="`new-card-title-${column.id}`"
        @keyup.enter="submitCard"
        @keyup.escape="cancelForm"
      />
      <textarea
        v-model="newDetails"
        placeholder="Details (optional)"
        :id="`new-card-details-${column.id}`"
        rows="2"
      />
      <div class="form-actions">
        <button class="btn-add-submit" :id="`submit-card-${column.id}`" @click="submitCard">Add card</button>
        <button class="btn-cancel" @click="cancelForm">Cancel</button>
      </div>
    </div>
    <button
      v-else
      class="btn-add-card"
      :id="`add-card-btn-${column.id}`"
      @click="showForm = true"
    >
      + Add card
    </button>
  </div>
</template>

<style scoped>
.column {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 3px solid var(--yellow);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  min-width: 240px;
  max-width: 300px;
  flex: 1;
  max-height: calc(100vh - 120px);
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  gap: 8px;
  flex-shrink: 0;
}

.column-name {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text);
  cursor: pointer;
  flex: 1;
  transition: color var(--transition);
}
.column-name:hover { color: var(--yellow); }

.column-name-input {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 4px 8px;
  flex: 1;
}

.card-count {
  background: var(--surface-2);
  color: var(--gray);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
  flex-shrink: 0;
}

.card-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 4px;
}

/* Drag-and-drop visual cues */
:deep(.drag-ghost) {
  opacity: 0.35;
  border: 2px dashed var(--blue);
  background: var(--surface-2);
}

:deep(.drag-chosen) {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  transform: rotate(1.5deg);
}

/* Add form */
.add-form {
  padding: 10px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.btn-add-submit {
  background: var(--purple);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  flex: 1;
}
.btn-add-submit:hover { opacity: 0.85; }

.btn-cancel {
  background: transparent;
  color: var(--gray);
  font-size: 13px;
  padding: 7px 10px;
  border-radius: var(--radius-sm);
}
.btn-cancel:hover { color: var(--text); background: var(--surface-2); }

.btn-add-card {
  background: transparent;
  color: var(--gray);
  font-size: 13px;
  font-weight: 500;
  padding: 10px 16px 14px;
  text-align: left;
  width: 100%;
  border-radius: 0 0 var(--radius) var(--radius);
  flex-shrink: 0;
  transition: color var(--transition), background var(--transition);
}
.btn-add-card:hover {
  color: var(--text);
  background: var(--surface-2);
}
</style>
