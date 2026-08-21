<template>
  <div class="mt-4 pt-3 border-t border-gray-200">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2">
        <button
          class="px-2 py-0.5 rounded font-medium text-xs transition"
          :class="activeTab === 'comments' ? 'bg-blue-50 text-blue-600 border border-blue-200' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'comments'"
        >
          讨论 / 评论 ({{ comments.length }})
        </button>
        <button
          class="px-2 py-0.5 rounded font-medium text-xs transition"
          :class="activeTab === 'activities' ? 'bg-blue-50 text-blue-600 border border-blue-200' : 'text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'activities'"
        >
          操作记录 ({{ activities.length }})
        </button>
      </div>
    </div>

    <!-- Comments List -->
    <div v-if="activeTab === 'comments'" class="space-y-2">
      <div v-if="comments.length === 0" class="text-gray-400 py-2 text-center text-xs">
        暂无讨论，快来发表第一条评论吧
      </div>
      <div
        v-for="c in comments"
        :key="c.id"
        class="bg-gray-50 p-2 rounded border border-gray-200 text-xs"
      >
        <div class="flex justify-between items-center text-gray-500 mb-1">
          <span class="font-medium text-gray-700">
            {{ c.user?.fullname || '匿名' }}
            <span class="text-gray-400 text-[10px] ml-1">({{ c.user?.role || 'user' }})</span>
          </span>
          <span class="text-[11px] text-gray-400">{{ formatDate(c.created_at) }}</span>
        </div>
        <div class="text-gray-800 whitespace-pre-wrap leading-relaxed">{{ c.content }}</div>
      </div>

      <!-- Add Comment Form -->
      <div class="mt-3">
        <textarea
          v-model="commentText"
          placeholder="添加讨论评论 (Ctrl+Enter 快捷发送)..."
          rows="2"
          class="w-full p-2 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-y"
          @keydown.ctrl.enter="submitComment"
        ></textarea>
        <div class="flex justify-between items-center mt-1">
          <span class="text-gray-400 text-[11px]">快捷键：Ctrl + Enter 发送</span>
          <button
            class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium disabled:opacity-50 transition"
            :disabled="!commentText.trim() || submitting"
            @click="submitComment"
          >
            {{ submitting ? '发送中...' : '发送讨论' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Activities Audit Trail -->
    <div v-else-if="activeTab === 'activities'" class="space-y-1.5 max-h-48 overflow-y-auto">
      <div v-if="activities.length === 0" class="text-gray-400 py-2 text-center text-xs">
        暂无操作记录
      </div>
      <div
        v-for="act in activities"
        :key="act.id"
        class="flex items-center justify-between text-xs py-1 border-b border-gray-100 last:border-0"
      >
        <div class="flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
          <span class="font-medium text-gray-700">{{ act.user?.fullname || '系统' }}</span>
          <span class="text-gray-600">{{ act.detail }}</span>
        </div>
        <span class="text-[11px] text-gray-400 whitespace-nowrap">{{ formatDate(act.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Comment, Activity } from '../types'
import { formatDate } from '../utils/formatter'
import client from '../api/client'

const props = defineProps<{
  bugId: number
  comments: Comment[]
  activities: Activity[]
}>()

const emit = defineEmits<{
  (e: 'comment-added', comment: Comment): void
}>()

const activeTab = ref<'comments' | 'activities'>('comments')
const commentText = ref('')
const submitting = ref(false)

async function submitComment() {
  if (!commentText.value.trim() || submitting.value) return
  submitting.value = true
  try {
    const res = await client.post(`/bugs/${props.bugId}/comments`, {
      content: commentText.value.trim()
    })
    emit('comment-added', res.data)
    commentText.value = ''
  } catch (e) {
    console.error('Failed to post comment', e)
  } finally {
    submitting.value = false
  }
}
</script>
