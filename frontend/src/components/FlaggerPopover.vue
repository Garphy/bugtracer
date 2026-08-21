<template>
  <div
    v-if="visible"
    ref="popoverRef"
    class="fixed z-50 bg-white border border-gray-300 rounded shadow-lg py-1 text-xs w-32 animate-in fade-in zoom-in-95 duration-100"
    :style="{ top: `${position.y}px`, left: `${position.x}px` }"
    @mouseenter="cancelClose"
    @mouseleave="startClose"
  >
    <div class="px-2 py-1 text-gray-400 border-b border-gray-100 font-medium">
      设为状态 (#{{ bugId }})
    </div>
    <ul>
      <li
        v-for="item in availableStatuses"
        :key="item.id"
        class="px-2 py-1 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-gray-700 hover:text-blue-600 transition"
        @click="selectStatus(item.id)"
      >
        <span class="flex items-center gap-1.5">
          <span :class="['w-2 h-2 rounded-full inline-block', getDotClass(item.code)]"></span>
          {{ item.name }}
        </span>
        <span v-if="currentStatus === item.id" class="text-blue-500 font-bold">✓</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { STATUS_LIST } from '../utils/formatter'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{
  bugId: number
  currentStatus: number
  position: { x: number; y: number }
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'select', status: number): void
  (e: 'close'): void
}>()

const authStore = useAuthStore()
const popoverRef = ref<HTMLElement | null>(null)
let closeTimer: any = null

const availableStatuses = computed(() => {
  if (authStore.isAdmin) return STATUS_LIST
  // Coder can change to fixed, part_fixed, wont_fix
  return STATUS_LIST
})

function getDotClass(code: string) {
  switch (code) {
    case 'closed': return 'bg-gray-400'
    case 'new': return 'bg-blue-500'
    case 'key': return 'bg-red-500'
    case 'part_fixed': return 'bg-amber-500'
    case 'fixed': return 'bg-green-500'
    case 'wont_fix': return 'bg-gray-300'
    case 'todo': return 'bg-purple-500'
    case 'idea': return 'bg-teal-500'
    default: return 'bg-gray-400'
  }
}

function selectStatus(status: number) {
  emit('select', status)
  emit('close')
}

function startClose() {
  clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    emit('close')
  }, 300)
}

function cancelClose() {
  clearTimeout(closeTimer)
}

function handleClickOutside(e: MouseEvent) {
  if (popoverRef.value && !popoverRef.value.contains(e.target as Node)) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  clearTimeout(closeTimer)
})
</script>
