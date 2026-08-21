<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 animate-in fade-in"
    @click.self="emit('close')"
  >
    <div class="bg-white rounded-lg shadow-2xl border border-gray-200 w-full max-w-md p-5 text-xs text-gray-700 animate-in zoom-in-95">
      <div class="flex justify-between items-center pb-2.5 mb-4 border-b border-gray-200">
        <h3 class="text-sm font-bold text-gray-800">个人设置与 API Key</h3>
        <button class="text-gray-400 hover:text-gray-600 text-base" @click="emit('close')">✕</button>
      </div>

      <!-- User Info -->
      <div class="bg-gray-50 p-3 rounded mb-4 space-y-1.5">
        <div class="flex justify-between">
          <span class="text-gray-500">用户名：</span>
          <span class="font-medium text-gray-800">{{ authStore.user?.username }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">全名/昵称：</span>
          <span class="font-medium text-gray-800">{{ authStore.user?.fullname }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">系统角色：</span>
          <span class="font-medium text-blue-600 uppercase">{{ authStore.user?.role }}</span>
        </div>
      </div>

      <!-- AI Agent / MCP API Key -->
      <div class="mb-4">
        <label class="block font-medium text-gray-700 mb-1">
          AI Agent / MCP 访问密钥 (API Key)
        </label>
        <div class="flex gap-1.5">
          <input
            type="text"
            readonly
            :value="authStore.user?.api_key || '暂无 Key'"
            class="flex-1 px-2.5 py-1.5 bg-gray-100 border border-gray-300 rounded font-mono text-[11px] select-all text-gray-600"
          />
          <button
            class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1.5 rounded font-medium transition"
            @click="copyApiKey"
          >
            {{ copySuccess ? '已复制!' : '复制' }}
          </button>
          <button
            class="bg-amber-100 hover:bg-amber-200 text-amber-800 px-2.5 py-1.5 rounded font-medium transition"
            title="重新生成密钥"
            @click="regenerateKey"
          >
            重置
          </button>
        </div>
        <p class="text-[11px] text-gray-400 mt-1">
          提示：供 Claude Desktop / Cursor / Antigravity 等 AI Agent 接入认证使用。
        </p>
      </div>

      <!-- Change Password -->
      <div class="border-t border-gray-200 pt-3">
        <h4 class="font-medium text-gray-800 mb-2">修改密码</h4>
        <div class="space-y-2">
          <div>
            <label class="block text-gray-500 mb-0.5">原密码：</label>
            <input
              v-model="oldPassword"
              type="password"
              class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              placeholder="请输入原密码"
            />
          </div>
          <div>
            <label class="block text-gray-500 mb-0.5">新密码：</label>
            <input
              v-model="newPassword"
              type="password"
              class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
              placeholder="至少4位新密码"
            />
          </div>
        </div>
        <div v-if="pwError" class="text-red-500 text-xs mt-1">{{ pwError }}</div>
        <div v-if="pwSuccess" class="text-green-600 text-xs mt-1">{{ pwSuccess }}</div>
        <div class="mt-3 text-right">
          <button
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded font-medium transition disabled:opacity-50"
            :disabled="!oldPassword || !newPassword || pwLoading"
            @click="handleChangePassword"
          >
            {{ pwLoading ? '修改中...' : '确认修改密码' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'

defineProps<{ visible: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const authStore = useAuthStore()
const copySuccess = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const pwLoading = ref(false)
const pwError = ref('')
const pwSuccess = ref('')

async function copyApiKey() {
  if (!authStore.user?.api_key) return
  await navigator.clipboard.writeText(authStore.user.api_key)
  copySuccess.value = true
  setTimeout(() => {
    copySuccess.value = false
  }, 2000)
}

async function regenerateKey() {
  if (!confirm('确定重新生成 API Key？老 Key 将立即失效！')) return
  try {
    const res = await client.post('/auth/regenerate-api-key')
    if (authStore.user) {
      authStore.user.api_key = res.data.api_key
      localStorage.setItem('bt_user', JSON.stringify(authStore.user))
    }
  } catch (e) {
    console.error('Failed to regenerate API key', e)
  }
}

async function handleChangePassword() {
  pwError.value = ''
  pwSuccess.value = ''
  pwLoading.value = true
  try {
    await client.post('/auth/change-password', {
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    pwSuccess.value = '密码修改成功！'
    oldPassword.value = ''
    newPassword.value = ''
    setTimeout(() => {
      pwSuccess.value = ''
      emit('close')
    }, 1500)
  } catch (e: any) {
    pwError.value = e.response?.data?.detail || '密码修改失败'
  } finally {
    pwLoading.value = false
  }
}
</script>
