import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '../api/client'
import { User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('bt_token'))
  const user = ref<User | null>(
    localStorage.getItem('bt_user') ? JSON.parse(localStorage.getItem('bt_user')!) : null
  )

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCoder = computed(() => user.value?.role === 'coder')
  const isTester = computed(() => user.value?.role === 'tester')

  async function login(username: string, password: string): Promise<boolean> {
    const res = await client.post('/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('bt_token', res.data.access_token)
    localStorage.setItem('bt_user', JSON.stringify(res.data.user))
    return true
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await client.get('/auth/me')
      user.value = res.data
      localStorage.setItem('bt_user', JSON.stringify(res.data))
    } catch (e) {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('bt_token')
    localStorage.removeItem('bt_user')
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    isCoder,
    isTester,
    login,
    fetchMe,
    logout
  }
})
