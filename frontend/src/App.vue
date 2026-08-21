<template>
  <div id="app-root">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  if (authStore.isAuthenticated) {
    authStore.fetchMe()
  }
})
</script>
