<template>
  <div class="relative flex items-center">
    <div class="relative flex items-center">
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Bug搜索 / 快捷语法 (按?查看提示)"
        class="h-7 w-64 px-2.5 pr-7 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 bg-white placeholder-gray-400"
        @keydown.enter="handleSearch"
        @focus="isFocused = true"
        @blur="handleBlur"
      />
      <button
        v-if="query"
        class="absolute right-2 text-gray-400 hover:text-gray-600 text-xs font-bold"
        title="清空"
        @click="clearSearch"
      >
        ×
      </button>
    </div>

    <button
      class="ml-1 text-gray-400 hover:text-blue-600 p-1"
      title="搜索语法帮助"
      @click="showHelp = !showHelp"
    >
      <HelpCircle class="w-4 h-4" />
    </button>

    <!-- Syntax Help Tooltip / Popover -->
    <div
      v-if="showHelp"
      class="absolute left-0 top-8 z-40 w-80 bg-white border border-gray-300 rounded shadow-xl p-3 text-xs text-gray-700 animate-in fade-in zoom-in-95"
    >
      <div class="flex justify-between items-center pb-1.5 mb-2 border-b border-gray-200">
        <span class="font-bold text-blue-600">BugTracer 快捷搜索语法</span>
        <button class="text-gray-400 hover:text-gray-600" @click="showHelp = false">✕</button>
      </div>
      <ul class="space-y-1.5 leading-relaxed text-gray-600">
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">102</code> 或 <code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">102,103</code> ：查找指定 ID（单 ID 自动打开详情）</li>
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">(用户ID)</code> ：查找此用户提出的 Bug</li>
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">{用户ID}</code> ：查找指派给此用户的 Bug</li>
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">!{用户ID}</code> ：查找非指派给此用户的 Bug</li>
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">{2026-1-1~2026-2-1}</code> ：按变更日期时间段查找</li>
        <li><code class="bg-gray-100 px-1 py-0.5 rounded text-blue-700">关键词</code> ：模糊匹配 Bug 描述与版本</li>
      </ul>
      <div class="mt-2.5 pt-2 border-t border-gray-100 text-right">
        <button
          class="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1 rounded text-xs"
          @click="showHelp = false"
        >
          知道了
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { HelpCircle } from 'lucide-vue-next'
import { useProjectStore } from '../stores/project'

const projectStore = useProjectStore()
const query = ref(projectStore.searchQuery)
const showHelp = ref(false)
const isFocused = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

watch(() => projectStore.searchQuery, (newVal) => {
  query.value = newVal
})

function handleSearch() {
  projectStore.setSearch(query.value)
}

function clearSearch() {
  query.value = ''
  projectStore.setSearch('')
}

function handleBlur() {
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}
</script>
