<script setup lang="ts">
import { onMounted } from 'vue'

const { fetchBoard, isBoardLoading } = useBoard()

onMounted(() => {
  fetchBoard()
})
</script>

<template>
  <div class="h-full">
    <div v-if="isBoardLoading" style="color:var(--gray-text); padding: 40px; text-align: center; font-size: 18px;">
      Loading Board State securely from SQLite...
    </div>
    <KanbanBoard v-else />
  </div>
</template>
