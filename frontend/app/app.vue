<script setup lang="ts">
useHead({
  title: 'Kanban Board',
  meta: [
    { name: 'description', content: 'A slick, professional Kanban project management board.' },
  ],
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
  ],
})
</script>

<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <h1 class="app-title">Kanban Board</h1>
        <div class="header-accent" />
      </div>
    </header>

    <!-- Board -->
    <main class="app-main">
      <KanbanBoard />
    </main>
  </div>
</template>

<style scoped>
.app-header {
  background: var(--navy);
  border-bottom: 3px solid var(--yellow);
  padding: 0 24px;
  flex-shrink: 0;
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 60px;
}

.app-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
}

.header-accent {
  height: 3px;
  width: 48px;
  background: var(--yellow);
  border-radius: 99px;
  margin-top: 2px;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  overflow: hidden;
}
</style>
