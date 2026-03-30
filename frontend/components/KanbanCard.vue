<script setup lang="ts">
import type { Card } from '~/composables/useBoard'

const props = defineProps<{
  card: Card
  columnId: string
}>()

const emit = defineEmits<{
  delete: [columnId: string, cardId: string]
}>()

const expanded = ref(false)
</script>

<template>
  <div class="card" :class="{ expanded }">
    <div class="card-header" @click="expanded = !expanded">
      <span class="card-title">{{ card.title }}</span>
      <button
        class="card-delete"
        :id="`delete-card-${card.id}`"
        title="Delete card"
        @click.stop="emit('delete', columnId, card.id)"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6l-1 14H6L5 6" />
          <path d="M10 11v6M14 11v6" />
          <path d="M9 6V4h6v2" />
        </svg>
      </button>
    </div>
    <p v-if="card.details" class="card-details" :class="{ 'line-clamp': !expanded }">
      {{ card.details }}
    </p>
  </div>
</template>

<style scoped>
.card {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  user-select: none;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  border-color: rgba(32, 157, 215, 0.3);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.card-title {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 1.4;
  color: var(--text);
  flex: 1;
}

.card-delete {
  background: transparent;
  color: var(--gray);
  padding: 2px;
  border-radius: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity var(--transition), color var(--transition), background var(--transition);
}

.card:hover .card-delete {
  opacity: 1;
}

.card-delete:hover {
  color: #ff5f5f;
  background: rgba(255, 95, 95, 0.12);
}

.card-details {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
  line-height: 1.5;
}

.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
