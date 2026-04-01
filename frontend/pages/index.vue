<script setup lang="ts">
import { onMounted } from 'vue'

const { fetchBoard, isBoardLoading, isError } = useBoard()

onMounted(() => {
  fetchBoard()
})
</script>

<template>
  <div class="h-full">
    <div v-if="isError" style="color:#ff5f5f; padding: 40px; text-align: center; font-size: 16px;">
      Could not load board. Check the server is running.
    </div>
    <div v-else-if="isBoardLoading" style="color:var(--gray-text); padding: 40px; text-align: center; font-size: 18px;">
      Loading your Kanban board...
    </div>
    <KanbanBoard v-else />
  </div>
</template>
