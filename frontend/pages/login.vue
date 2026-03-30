<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const errorMsg = ref('')

const auth = useCookie('kanban_auth')

function handleLogin() {
  if (username.value === 'user' && password.value === 'password') {
    auth.value = 'admin_token_active'
    navigateTo('/')
  } else {
    errorMsg.value = 'Invalid username or password'
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">Sign In</h2>
      <p class="login-subtitle">Access your project workspace</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label>Username</label>
          <input type="text" v-model="username" placeholder="Enter 'user'" />
        </div>
        
        <div class="input-group">
          <label>Password</label>
          <input type="password" v-model="password" placeholder="Enter 'password'" />
        </div>
        
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        
        <button type="submit" class="submit-btn">Login</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding-bottom: 100px;
}

.login-card {
  background: var(--navy);
  border: 1px solid var(--gray-border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 40px 32px;
  width: 100%;
  max-width: 400px;
}

.login-title {
  font-size: 26px;
  color: #fff;
  margin-bottom: 8px;
  font-weight: 700;
  text-align: center;
}

.login-subtitle {
  color: var(--gray-text);
  font-size: 15px;
  margin-bottom: 32px;
  text-align: center;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--gray-border);
  border-radius: 6px;
  font-size: 15px;
  outline: none;
  background: #fff;
  color: #111; /* Force dark text color inside the white input */
  transition: border-color 0.2s;
}

.input-group input:focus {
  border-color: var(--blue);
}

.error-msg {
  color: #fff;
  background: rgba(211, 47, 47, 0.8);
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 20px;
  font-weight: 500;
  text-align: center;
}

.submit-btn {
  width: 100%;
  background: var(--purple);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 8px;
}

.submit-btn:hover {
  opacity: 0.9;
}
</style>
