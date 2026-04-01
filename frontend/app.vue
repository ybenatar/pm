<script setup lang="ts">
import { ref } from 'vue'
const auth = useCookie('kanban_auth')
const { columns, isBoardLoading } = useBoard()

useHead({
  title: 'Kanban Board',
  meta: [
    { name: 'description', content: 'A slick, professional Kanban project management board.' },
  ],
  link: [
    { rel: 'icon', href: 'data:,' },
  ],
})

const isSidebarOpen = ref(true)

function logout() {
  auth.value = null
  columns.value = []
  isBoardLoading.value = true
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
        <button v-if="auth && !isSidebarOpen" class="icon-btn" title="Open AI assistant" @click="isSidebarOpen = true">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M3 3h18v2H3V3zm0 4h12v2H3V7zm0 4h18v2H3v-2zm0 4h12v2H3v-2zm0 4h18v2H3v-2z" />
          </svg>
        </button>
        <button v-if="auth && isSidebarOpen" class="icon-btn" title="Close AI assistant" @click="isSidebarOpen = false">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M3 3h18v2H3V3zm0 4h12v2H3V7zm0 4h18v2H3v-2zm0 4h12v2H3v-2zm0 4h18v2H3v-2z" />
          </svg>
        </button>
        <button v-if="auth" class="icon-btn logout-btn" title="Logout" @click="logout">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" />
          </svg>
        </button>
      </div>
    </header>

    <!-- App Body (Main + Sidebar) -->
    <div class="app-body">
      <main class="app-main">
        <NuxtPage />
      </main>
      
      <!-- AI Sidebar -->
      <transition name="slide">
        <AIChatSidebar v-if="auth && isSidebarOpen" />
      </transition>
    </div>

  </div>
</template>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

.app-header {
  background: var(--navy);
  border-bottom: 3px solid var(--yellow);
  padding: 0 24px;
  flex-shrink: 0;
  z-index: 20;
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

.icon-btn {
  background: transparent;
  border: none;
  color: var(--gray-text);
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.2s, background 0.2s;
}

.icon-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.08);
}

.logout-btn {
  margin-left: 4px;
}

.app-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  overflow: hidden;
}

/* Transitions */
.slide-enter-active, .slide-leave-active {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
