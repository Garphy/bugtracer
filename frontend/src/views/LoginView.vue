<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="bg-white border border-gray-300 rounded-lg shadow-xl w-full max-w-sm p-6 space-y-4">
      <div class="text-center pb-2 border-b border-gray-200">
        <h1 class="text-lg font-bold text-gray-900 tracking-wide">BugTracer 2.0</h1>
        <p class="text-xs text-gray-500 mt-0.5">极速缺陷追踪与研发支撑系统</p>
      </div>

      <form class="space-y-3" @submit.prevent="handleLogin">
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">账号：</label>
          <input
            v-model="username"
            type="text"
            required
            autocomplete="username"
            class="w-full h-8 px-2.5 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="请输入账号 (如: admin)"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">密码：</label>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full h-8 px-2.5 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="请输入密码"
          />
        </div>

        <div v-if="errorMsg" class="text-red-500 text-xs font-medium">
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-1.5 rounded text-xs transition disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="bg-blue-50 border border-blue-200 rounded p-2 text-[11px] text-blue-800 leading-relaxed">
        <strong>默认管理员：</strong> 账号 <code class="font-mono bg-white px-1 rounded">admin</code> / 密码 <code class="font-mono bg-white px-1 rounded">123456</code>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('admin')
const password = ref('123456')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  if (!username.value || !password.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    const ok = await authStore.login(username.value.trim(), password.value)
    if (ok) {
      router.push('/')
    }
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || '登录失败，请检查账号密码'
  } finally {
    loading.value = false
  }
}
</script>
