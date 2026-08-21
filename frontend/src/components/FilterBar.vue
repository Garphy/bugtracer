<template>
  <div class="flex flex-wrap items-center justify-between gap-2 py-1.5 px-3 bg-gray-50 border-b border-gray-200 text-xs text-gray-700">
    <div class="flex items-center gap-3">
      <SearchBar />
      <span class="text-gray-500 whitespace-nowrap">
        显示：<strong class="text-gray-800">{{ projectStore.totalBugs }}</strong> / {{ projectStore.totalProjectBugs }}
      </span>
    </div>

    <div class="flex items-center gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <span class="text-gray-500 font-medium">状态：</span>
        <label
          v-for="status in STATUS_LIST"
          :key="status.id"
          class="flex items-center gap-1 cursor-pointer select-none hover:text-blue-600 transition"
          :title="`双击仅筛选【${status.name}】`"
          @dblclick.prevent="handleDoubleClick(status.id)"
        >
          <input
            type="checkbox"
            :value="status.id"
            :checked="selectedStatuses.includes(status.id)"
            class="rounded border-gray-300 text-blue-600 focus:ring-0 cursor-pointer"
            @change="handleCheckboxChange(status.id, $event)"
          />
          <span :class="getStatusBadgeClass(status.code)">
            {{ status.name }}
          </span>
        </label>
      </div>

      <div class="flex items-center gap-1.5 text-xs text-blue-600">
        <button class="hover:underline" @click="selectAll">全选</button>
        <span class="text-gray-300">/</span>
        <button class="hover:underline" @click="deselectAll">不选</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import SearchBar from './SearchBar.vue'
import { STATUS_LIST } from '../utils/formatter'
import { useProjectStore } from '../stores/project'

const projectStore = useProjectStore()
const selectedStatuses = ref<number[]>([...projectStore.statusFilter])

watch(() => projectStore.statusFilter, (newVal) => {
  selectedStatuses.value = [...newVal]
})

function getStatusBadgeClass(code: string) {
  return `status-badge status-${code} text-[11px] py-0 px-1.5`
}

function handleCheckboxChange(statusId: number, event: Event) {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    if (!selectedStatuses.value.includes(statusId)) {
      selectedStatuses.value.push(statusId)
    }
  } else {
    selectedStatuses.value = selectedStatuses.value.filter(id => id !== statusId)
  }
  projectStore.setStatusFilter(selectedStatuses.value)
}

function handleDoubleClick(statusId: number) {
  selectedStatuses.value = [statusId]
  projectStore.setStatusFilter([statusId])
}

function selectAll() {
  selectedStatuses.value = STATUS_LIST.map(s => s.id)
  projectStore.setStatusFilter(selectedStatuses.value)
}

function deselectAll() {
  selectedStatuses.value = []
  projectStore.setStatusFilter([])
}
</script>
