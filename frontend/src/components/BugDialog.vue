<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-start justify-center pt-10 pb-10 overflow-y-auto bg-black bg-opacity-40 animate-in fade-in"
    @click.self="handleClose"
    @paste="handlePaste"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <div
      class="bg-white rounded-md shadow-2xl border border-gray-300 w-full max-w-2xl text-xs text-gray-700 animate-in zoom-in-95 my-auto relative"
      :class="{ 'ring-2 ring-blue-500 bg-blue-50': isDragging }"
    >
      <!-- Drag overlay indicator -->
      <div v-if="isDragging" class="absolute inset-0 bg-blue-100 bg-opacity-80 flex items-center justify-center rounded-md z-20 pointer-events-none">
        <div class="text-blue-700 font-bold text-sm flex items-center gap-2">
          <UploadCloud class="w-6 h-6 animate-bounce" /> 释放文件自动上传附件
        </div>
      </div>

      <!-- Top Header -->
      <div class="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-200 rounded-t-md">
        <div class="flex items-center gap-2">
          <span class="font-bold text-gray-800 text-sm">
            {{ isNew ? '提交新 Bug' : `Bug #${bugData?.id}` }}
          </span>
          <span v-if="!isNew && bugData?.creator" class="text-gray-500 text-[11px]">
            posted by <strong class="text-gray-700">{{ bugData.creator.fullname }}</strong>
            <span v-if="bugData.last_changer"> / Updated by {{ bugData.last_changer.fullname }}</span>
            <span class="ml-1 text-gray-400">@{{ formatShortDate(bugData.updated_at) }}</span>
          </span>
        </div>

        <div class="flex items-center gap-3">
          <!-- Roll navigation -->
          <div v-if="!isNew" class="flex items-center gap-1.5 text-blue-600 text-[11px]">
            <button class="hover:underline hover:text-blue-800 disabled:opacity-30" :disabled="!hasPrev" @click="navigateRoll('prev')">
              &lt; 上一条
            </button>
            <span class="text-gray-300">|</span>
            <button class="hover:underline hover:text-blue-800 disabled:opacity-30" :disabled="!hasNext" @click="navigateRoll('next')">
              下一条 &gt;
            </button>
          </div>
          <button class="text-gray-400 hover:text-gray-700 text-sm font-bold px-1" title="关闭 (Esc)" @click="handleClose">
            ✕
          </button>
        </div>
      </div>

      <!-- Form Body -->
      <div class="p-4 space-y-3">
        <!-- Row 1: Module & Status -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-gray-600 font-medium mb-1">所属模块：</label>
            <select
              v-model="form.module_id"
              class="w-full h-7 px-2 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 bg-white"
            >
              <option :value="undefined">- 所属模块 -</option>
              <option
                v-for="m in projectStore.currentProjectDetail?.modules || []"
                :key="m.id"
                :value="m.id"
              >
                {{ m.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-gray-600 font-medium mb-1">Bug 状态：</label>
            <select
              v-model="form.status"
              class="w-full h-7 px-2 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 bg-white font-medium"
            >
              <option v-for="s in STATUS_LIST" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.code }})
              </option>
            </select>
          </div>
        </div>

        <!-- Row 2: Description / Content -->
        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="text-gray-600 font-medium">Bug 描述 (支持 Markdown & 图文混排)：</label>
            <div class="flex items-center gap-2">
              <button
                v-if="isNew || isEditingContent"
                type="button"
                class="text-blue-600 hover:underline text-[11px] font-medium"
                @click="showPreview = !showPreview"
              >
                [{{ showPreview ? '切换编辑' : '实时预览 Markdown' }}]
              </button>
              <button
                v-if="!isNew && !isEditingContent"
                type="button"
                class="text-blue-600 hover:underline text-[11px] font-medium"
                @click="isEditingContent = true"
              >
                [编辑描述]
              </button>
            </div>
          </div>

          <!-- View Mode (Formatted with markdown & images) -->
          <div
            v-if="(!isNew && !isEditingContent) || showPreview"
            class="min-h-[90px] max-h-72 overflow-y-auto p-3 bg-gray-50 border border-gray-200 rounded text-gray-800 leading-relaxed break-words"
            v-html="renderedContent"
          ></div>

          <!-- Edit Mode -->
          <div v-else>
            <textarea
              ref="contentInputRef"
              v-model="form.content"
              rows="5"
              placeholder="请输入详细描述（支持 Markdown 标题/列表/代码块、[b]加粗红字[/b]、输入「图1」或「![图1]」自动嵌入附件、支持 Ctrl+V 截图直接粘贴）..."
              class="w-full p-2.5 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 leading-relaxed font-sans"
              @keydown.ctrl.enter="handleSubmit"
            ></textarea>
            <div class="flex justify-between text-[11px] text-gray-400 mt-0.5">
              <span>快捷提示：输入「图1」、「图2」或「![图1]」自动嵌入对应附件</span>
              <span>Ctrl + Enter 快捷提交</span>
            </div>
          </div>
        </div>

        <!-- Row 3: Version & Assignee -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-gray-600 font-medium mb-1">版本：</label>
            <input
              v-model="form.ver"
              type="text"
              class="w-full h-7 px-2 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500"
              placeholder="如 v1.0.0"
            />
          </div>

          <div>
            <label class="block text-gray-600 font-medium mb-1">指派给：</label>
            <select
              v-model="form.assignee_id"
              class="w-full h-7 px-2 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 bg-white"
            >
              <option :value="0">- 未指派 -</option>
              <option
                v-for="u in assignableUsers"
                :key="u.id"
                :value="u.id"
              >
                {{ u.fullname }} ({{ u.role }})
              </option>
            </select>
          </div>
        </div>

        <!-- Row 4: Attachments Area -->
        <div class="bg-gray-50 border border-gray-200 rounded p-2.5">
          <div class="flex justify-between items-center mb-1.5">
            <span class="font-medium text-gray-700 flex items-center gap-1">
              <Paperclip class="w-3.5 h-3.5 text-gray-500" />
              附件列表 ({{ attachments.length }})
            </span>
            <label class="cursor-pointer text-blue-600 hover:underline text-[11px] flex items-center gap-0.5">
              <Upload class="w-3 h-3" />
              <span>上传文件 / 截图直接 Ctrl+V</span>
              <input type="file" multiple class="hidden" @change="handleFileInput" />
            </label>
          </div>

          <!-- Attachments list -->
          <ul v-if="attachments.length > 0" class="space-y-1">
            <li
              v-for="(att, idx) in attachments"
              :key="att.id || att.stored_name"
              class="flex items-center justify-between py-0.5 px-1.5 bg-white border border-gray-200 rounded text-xs"
            >
              <div class="flex items-center gap-1.5 truncate max-w-sm">
                <span class="text-blue-600 font-bold">图{{ idx + 1 }}：</span>
                <a :href="att.url" target="_blank" class="hover:underline text-gray-700 truncate">
                  {{ att.original_name }}
                </a>
              </div>
              <div class="flex items-center gap-2 text-[11px]">
                <a :href="att.url" target="_blank" class="text-blue-600 hover:underline">[查看]</a>
                <button class="text-red-500 hover:underline" @click="removeAttachment(idx, att)">[删除]</button>
              </div>
            </li>
          </ul>
          <div v-else class="text-gray-400 text-center py-1.5 text-[11px]">
            拖拽文件到此处，或使用截图工具后直接 <kbd class="px-1 py-0.5 bg-white border border-gray-300 rounded font-mono">Ctrl + V</kbd> 粘贴
          </div>
        </div>

        <!-- Comments & Activity (View Mode only) -->
        <CommentTimeline
          v-if="!isNew && bugData"
          :bug-id="bugData.id"
          :comments="bugData.comments || []"
          :activities="bugData.activities || []"
          @comment-added="handleCommentAdded"
        />

        <!-- Action Bar -->
        <div class="flex items-center justify-between pt-2 border-t border-gray-200">
          <span v-if="errorMessage" class="text-red-500 font-medium text-xs">{{ errorMessage }}</span>
          <span v-else class="text-gray-400 text-[11px]">快捷键：^Enter 提交；Esc 关闭</span>

          <div class="flex items-center gap-2">
            <button
              class="px-3 py-1.5 border border-gray-300 hover:bg-gray-100 rounded text-gray-700 font-medium transition"
              @click="handleClose"
            >
              取消
            </button>
            <button
              class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium disabled:opacity-50 transition flex items-center gap-1"
              :disabled="submitting || uploadLoading"
              @click="handleSubmit"
            >
              <span v-if="submitting || uploadLoading" class="animate-spin mr-1">⏳</span>
              <span>{{ isNew ? '提交新 Bug' : '保存修改' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { Paperclip, Upload, UploadCloud } from 'lucide-vue-next'
import { BugDetail, Attachment, UserSimple, Comment } from '../types'
import { STATUS_LIST, formatBugContent, formatShortDate } from '../utils/formatter'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'
import CommentTimeline from './CommentTimeline.vue'
import client from '../api/client'

const props = defineProps<{
  visible: boolean
  bugId: number | null // null = new bug
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', bugId: number): void
  (e: 'navigate', direction: 'prev' | 'next'): void
}>()

const projectStore = useProjectStore()
const authStore = useAuthStore()

const isNew = computed(() => !props.bugId || props.bugId === 0)
const bugData = ref<BugDetail | null>(null)
const isEditingContent = ref(false)
const showPreview = ref(false)
const isDragging = ref(false)
const submitting = ref(false)
const uploadLoading = ref(false)
const errorMessage = ref('')
const contentInputRef = ref<HTMLTextAreaElement | null>(null)

const form = reactive({
  module_id: undefined as number | undefined,
  status: 1,
  ver: '',
  content: '',
  assignee_id: 0,
  priority: 0
})

const attachments = ref<Attachment[]>([])
const allUsers = ref<UserSimple[]>([])

const assignableUsers = computed(() => {
  if (projectStore.currentProjectDetail?.members && projectStore.currentProjectDetail.members.length > 0) {
    return projectStore.currentProjectDetail.members
  }
  return allUsers.value
})

const renderedContent = computed(() => {
  return formatBugContent(form.content, attachments.value)
})

const currentBugIndex = computed(() => {
  if (!props.bugId) return -1
  return projectStore.bugs.findIndex(b => b.id === props.bugId)
})

const hasPrev = computed(() => currentBugIndex.value > 0)
const hasNext = computed(() => currentBugIndex.value !== -1 && currentBugIndex.value < projectStore.bugs.length - 1)

watch(() => props.visible, async (val) => {
  if (val) {
    errorMessage.value = ''
    await fetchUsers()
    if (props.bugId) {
      await loadBugDetail(props.bugId)
    } else {
      initNewBug()
    }
  }
})

watch(() => props.bugId, async (newId) => {
  if (props.visible && newId) {
    await loadBugDetail(newId)
  }
})

async function fetchUsers() {
  try {
    const res = await client.get('/auth/users')
    allUsers.value = res.data
  } catch (e) {}
}

function initNewBug() {
  bugData.value = null
  isEditingContent.value = true
  showPreview.value = false
  form.module_id = projectStore.currentModuleId || (projectStore.currentProjectDetail?.modules[0]?.id)
  form.status = 1
  form.ver = projectStore.currentProject?.default_version || ''
  form.content = ''
  form.assignee_id = 0
  form.priority = 0
  attachments.value = []
  nextTick(() => {
    contentInputRef.value?.focus()
  })
}

async function loadBugDetail(id: number) {
  try {
    const res = await client.get<BugDetail>(`/bugs/${id}`)
    bugData.value = res.data
    form.module_id = res.data.module_id
    form.status = res.data.status
    form.ver = res.data.ver
    form.content = res.data.content
    form.assignee_id = res.data.assignee_id || 0
    form.priority = res.data.priority || 0
    attachments.value = [...(res.data.attachments || [])]
    isEditingContent.value = false
    showPreview.value = false
  } catch (e: any) {
    errorMessage.value = '加载 Bug 详情失败'
  }
}

function navigateRoll(dir: 'prev' | 'next') {
  emit('navigate', dir)
}

function handleClose() {
  emit('close')
}

function handleCommentAdded(c: Comment) {
  if (bugData.value) {
    bugData.value.comments.push(c)
  }
}

// Attachment Uploading (File input, Drag & Drop, Clipboard Paste)
async function uploadFiles(files: FileList | File[]) {
  if (!files || files.length === 0) return
  uploadLoading.value = true
  errorMessage.value = ''
  try {
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const formData = new FormData()
      formData.append('file', file)
      formData.append('project_id', projectStore.currentProjectId.toString())
      if (props.bugId) {
        formData.append('bug_id', props.bugId.toString())
      }

      const res = await client.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (res.data.success) {
        attachments.value.push({
          id: res.data.id,
          project_id: projectStore.currentProjectId,
          original_name: res.data.original_name,
          stored_name: res.data.filename,
          file_size: file.size,
          mime_type: file.type,
          url: res.data.url
        })
      } else {
        errorMessage.value = res.data.error || '上传失败'
      }
    }
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || '上传文件失败'
  } finally {
    uploadLoading.value = false
    isDragging.value = false
  }
}

function handleFileInput(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files) {
    uploadFiles(target.files)
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files) {
    uploadFiles(e.dataTransfer.files)
  }
}

function handlePaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return

  const imageFiles: File[] = []
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.indexOf('image') !== -1) {
      const file = items[i].getAsFile()
      if (file) {
        // Name screenshot
        const namedFile = new File([file], `screenshot_${Date.now()}.png`, { type: 'image/png' })
        imageFiles.push(namedFile)
      }
    }
  }

  if (imageFiles.length > 0) {
    uploadFiles(imageFiles)
  }
}

async function removeAttachment(index: number, att: Attachment) {
  if (!confirm(`确定删除附件【${att.original_name}】？`)) return
  if (att.id) {
    try {
      await client.delete(`/upload/${att.id}`)
    } catch (e) {}
  }
  attachments.value.splice(index, 1)
}

async function handleSubmit() {
  if (!form.content.trim()) {
    errorMessage.value = '请填写 Bug 描述'
    return
  }
  submitting.value = true
  errorMessage.value = ''

  try {
    const attachmentIds = attachments.value.map(a => a.id).filter(id => !!id) as number[]
    const fileNames = attachments.value.map(a => a.stored_name)

    if (isNew.value) {
      const res = await client.post('/bugs', {
        project_id: projectStore.currentProjectId,
        module_id: form.module_id,
        ver: form.ver,
        content: form.content.trim(),
        assignee_id: form.assignee_id,
        priority: form.priority,
        status: form.status,
        attachment_ids: attachmentIds,
        files: fileNames
      })
      emit('saved', res.data.id)
    } else {
      const res = await client.put(`/bugs/${props.bugId}`, {
        project_id: projectStore.currentProjectId,
        module_id: form.module_id,
        ver: form.ver,
        content: form.content.trim(),
        assignee_id: form.assignee_id,
        priority: form.priority,
        status: form.status,
        attachment_ids: attachmentIds,
        files: fileNames
      })
      emit('saved', res.data.id)
    }
    emit('close')
  } catch (e: any) {
    errorMessage.value = e.response?.data?.detail || '提交失败'
  } finally {
    submitting.value = false
  }
}
</script>
