<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useBoard } from '~/composables/useBoard'
const { setBoard, triggerRefresh } = useBoard()

const messages = ref<{role: 'user' | 'assistant', text: string}[]>([])
const input = ref('')
const isLoading = ref(false)
const scrollContainer = ref<HTMLElement | null>(null)

// Load history from localStorage on mount
onMounted(() => {
  const savedMessages = localStorage.getItem('pm_ai_history')
  if (savedMessages) {
    messages.value = JSON.parse(savedMessages)
  } else {
    // AI Welcome Message (First load only)
    messages.value.push({
      role: 'assistant',
      text: "Hello! I'm your AI Kanban assistant. I can help you create, move, or delete cards. Try saying 'Add a card buy milk to To Do'!"
    })
    saveMessages()
  }
})

function saveMessages() {
  localStorage.setItem('pm_ai_history', JSON.stringify(messages.value))
}

function clearChat() {
  messages.value = [{
    role: 'assistant',
    text: "Chat cleared! How can I help you next?"
  }]
  saveMessages()
}

const scrollToBottom = async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return
  
  const userText = input.value
  messages.value.push({ role: 'user', text: userText })
  input.value = ''
  isLoading.value = true
  scrollToBottom()
  saveMessages()

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })
    
    if (!res.ok) throw new Error('Network error')
    
    const data = await res.json()
    
    // Update local chat
    messages.value.push({ role: 'assistant', text: data.text })
    saveMessages()
    
    // Sync the board state if returned
    if (data.board && data.board.columns) {
      setBoard(data.board.columns)
      triggerRefresh()
    }
  } catch (error) {
    messages.value.push({ role: 'assistant', text: "Sorry, I had trouble connecting to the brain. Please try again." })
    console.error('AI chat failed:', error)
    saveMessages()
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="ai-sidebar">
    <div class="sidebar-header">
      <div class="header-icon">AI</div>
      <h3>Kanban Assistant</h3>
      <div class="header-spacer"></div>
      <button class="clear-btn" title="Clear Chat" @click="clearChat">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19V4M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
        </svg>
      </button>
    </div>

    <!-- Messages List -->
    <div ref="scrollContainer" class="messages-container">
      <div 
        v-for="(msg, i) in messages" 
        :key="i" 
        :class="['message-bubble', msg.role]"
      >
        <div class="bubble-content">
          {{ msg.text }}
        </div>
      </div>
      
      <!-- Typing Indicator -->
      <div v-if="isLoading" class="message-bubble assistant typing">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-container">
      <textarea
        v-model="input"
        placeholder="Ask AI to manage cards..."
        @keydown.enter.prevent="sendMessage"
        rows="1"
      ></textarea>
      <button class="send-btn" :disabled="isLoading" @click="sendMessage">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.ai-sidebar {
  width: 320px;
  height: 100%;
  background: #fff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 15px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 16px;
  background: var(--navy);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.header-icon {
  background: var(--yellow);
  color: var(--navy);
  font-weight: 800;
  font-size: 12px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.sidebar-header h3 {
  font-size: 16px;
  margin: 0;
  font-weight: 600;
}

.header-spacer {
  flex: 1;
}

.clear-btn {
  background: transparent;
  border: none;
  color: #fff;
  opacity: 0.6;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: opacity 0.2s;
}

.clear-btn:hover {
  opacity: 1;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
  position: relative;
}

.message-bubble.assistant {
  align-self: flex-start;
  background: #f0f4f8;
  color: var(--navy);
  border-bottom-left-radius: 2px;
}

.message-bubble.user {
  align-self: flex-end;
  background: var(--purple-secondary, #753991);
  color: #fff;
  border-bottom-right-radius: 2px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: var(--navy);
  border-radius: 50%;
  opacity: 0.4;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

.input-container {
  padding: 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

textarea {
  flex: 1;
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  max-height: 100px;
  color: #032147 !important; /* Hardcoded Dark Navy for high contrast */
  caret-color: #032147 !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}

textarea::placeholder {
  color: #888888; /* Gray for placeholder */
}

textarea:focus {
  outline: none;
  border-color: var(--blue-primary);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(32, 157, 215, 0.2); /* Clear visual focus ring */
}

.send-btn {
  background: var(--purple-secondary, #753991);
  color: #fff;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
  flex-shrink: 0;
}

.send-btn:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
