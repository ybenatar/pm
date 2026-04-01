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
        <button v-if="auth" class="logout-btn" @click="logout">Logout</button>
        <button v-if="auth && isSidebarOpen" class="close-sidebar-btn" @click="isSidebarOpen = false">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
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

    <!-- Floating AI Bubble (Visible when sidebar is closed) -->
    <transition name="fade">
      <button v-if="auth && !isSidebarOpen" class="ai-floating-bubble" @click="isSidebarOpen = true">
        <div class="bubble-icon">AI</div>
        <div class="bubble-pulse"></div>
      </button>
    </transition>
  </div>
</template>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f4f7f9;
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

.close-sidebar-btn {
  background: transparent;
  border: none;
  color: #fff;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-sidebar-btn:hover {
  opacity: 1;
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

/* Floating AI Bubble */
.ai-floating-bubble {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  background: var(--purple-secondary);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 8px 30px rgba(117, 57, 145, 0.4);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.ai-floating-bubble:hover {
  transform: scale(1.1) translateY(-5px);
}

.bubble-icon {
  font-weight: 800;
  font-size: 18px;
  z-index: 2;
}

.bubble-pulse {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: var(--purple-secondary);
  opacity: 0.4;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.4; }
  100% { transform: scale(1.6); opacity: 0; }
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
