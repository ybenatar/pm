<script setup lang="ts">
const auth = useCookie('kanban_auth')

useHead({
  title: 'Kanban Board',
  meta: [
    { name: 'description', content: 'A slick, professional Kanban project management board.' },
  ],
  link: [
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
  ],
})

function logout() {
  auth.value = null
  navigateTo('/login')
}
</script>

<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <h1 class="app-title">Kanban Board</h1>
        <div class="header-accent" />
        
        <div class="header-spacer" />
        <button v-if="auth" class="logout-btn" @click="logout">Logout</button>
      </div>
    </header>

    <!-- Page Content -->
    <main class="app-main">
      <NuxtPage />
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

.header-spacer {
  flex: 1;
}

.logout-btn {
  background: transparent;
  color: var(--gray-text);
  border: 1px solid var(--gray-border);
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  overflow: hidden;
}
</style>
