<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-between">
    <!-- Top Header Bar -->
    <div>
      <header class="bg-gray-800 text-gray-200 px-4 py-2 flex flex-wrap items-center justify-between text-xs border-b border-gray-700">
        <!-- Left: Login user & Mode -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-gray-400">登录身份:</span>
            <strong class="text-white">{{ authStore.user?.fullname }} ({{ authStore.user?.username }})</strong>
            <button class="text-blue-400 hover:underline ml-1" @click="showProfileModal = true">[设置/Key]</button>
            <button class="text-red-400 hover:underline ml-1" @click="handleLogout">[退出]</button>
          </div>

          <!-- Mode Switch (Admin only) -->
          <div v-if="authStore.isAdmin" class="flex items-center gap-1 bg-gray-700 px-2 py-0.5 rounded text-gray-300">
            <span>当前：<strong class="text-white">{{ projectStore.mode === 'admin' ? '管理模式' : 'Debug模式' }}</strong></span>
            <button class="text-yellow-400 hover:underline ml-1" @click="projectStore.toggleMode()">
              [切{{ projectStore.mode === 'admin' ? 'Debug模式' : '管理模式' }}]
            </button>
          </div>
        </div>

        <!-- Right: Projects Dropdown & Navigation -->
        <div class="flex items-center gap-3">
          <!-- Project Switcher -->
          <div class="relative">
            <button
              class="flex items-center gap-1 bg-gray-700 hover:bg-gray-600 px-2.5 py-1 rounded text-white font-medium transition"
              @click="showProjectMenu = !showProjectMenu"
            >
              <span>总活动Bug <em class="text-yellow-400 not-italic font-bold">({{ projectStore.totalActiveBugsCount }})</em></span>
              <span class="text-gray-400">|</span>
              <span>当前项目：<strong>{{ projectStore.currentProject?.name || '选择项目' }}</strong> ({{ projectStore.currentProject?.active_bugs_count || 0 }})</span>
              <ChevronDown class="w-3.5 h-3.5 ml-0.5" />
            </button>

            <!-- Project Menu Dropdown -->
            <div
              v-if="showProjectMenu"
              class="absolute right-0 top-8 z-40 w-56 bg-white border border-gray-200 rounded shadow-xl py-1 text-gray-800 animate-in fade-in"
            >
              <div class="px-3 py-1 text-gray-400 font-medium text-[11px] border-b border-gray-100">选择切换项目</div>
              <ul class="max-h-60 overflow-y-auto">
                <li
                  v-for="p in projectStore.projects"
                  :key="p.id"
                  class="px-3 py-1.5 hover:bg-blue-50 cursor-pointer flex justify-between items-center transition"
                  :class="{ 'bg-blue-50 text-blue-600 font-bold': p.id === projectStore.currentProjectId }"
                  @click="handleSelectProject(p.id)"
                >
                  <span class="truncate">{{ p.name }}</span>
                  <span class="text-xs text-gray-400 font-normal">({{ p.active_bugs_count }})</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Top Navigation Links -->
          <router-link to="/report" class="text-gray-300 hover:text-white transition">项目报表</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin" class="text-gray-300 hover:text-white transition">管理后台</router-link>
        </div>
      </header>

      <!-- Main Workspace Container -->
      <main class="max-w-6xl mx-auto my-3 bg-white border border-gray-300 rounded shadow-sm overflow-hidden">
        <!-- Module Tabs Bar -->
        <div class="bg-gray-100 border-b border-gray-300 px-3 flex flex-wrap items-center justify-between">
          <ul class="flex items-center flex-wrap gap-0.5 text-xs">
            <li>
              <button
                class="px-3 py-2 font-medium transition border-b-2"
                :class="projectStore.currentModuleId === null ? 'border-blue-600 text-blue-600 bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
                @click="projectStore.selectModule(null)"
              >
                全部模块
              </button>
            </li>
            <li
              v-for="m in projectStore.currentProjectDetail?.modules || []"
              :key="m.id"
            >
              <button
                class="px-3 py-2 font-medium transition border-b-2"
                :class="projectStore.currentModuleId === m.id ? 'border-blue-600 text-blue-600 bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
                @click="projectStore.selectModule(m.id)"
              >
                {{ m.name }}
                <span v-if="m.bug_count" class="text-[10px] text-gray-400 ml-0.5">({{ m.bug_count }})</span>
              </button>
            </li>
          </ul>

          <button
            class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium flex items-center gap-1 transition shadow-sm my-1"
            title="快捷键：Ctrl + `"
            @click="openNewBugDialog"
          >
            <span>+ 提交新 Bug</span>
            <kbd class="hidden sm:inline text-[10px] bg-blue-700 px-1 rounded">^`</kbd>
          </button>
        </div>

        <!-- Filter Bar Component -->
        <FilterBar />

        <!-- High-Density Bug List -->
        <div class="relative min-h-[300px]">
          <div v-if="projectStore.loading" class="absolute inset-0 bg-white bg-opacity-60 flex items-center justify-center z-10">
            <span class="text-blue-600 font-medium text-xs animate-pulse">正在加载 Bug 列表...</span>
          </div>

          <ul v-if="projectStore.bugs.length > 0" class="divide-y divide-gray-100">
            <li
              v-for="bug in projectStore.bugs"
              :key="bug.id"
              class="bug-row px-3 flex items-center justify-between text-xs select-none cursor-pointer transition"
              :class="{
                'opacity-60 bg-gray-50': bug.status === 0 || bug.status === 5,
                'border-l-4 border-blue-500': bug.is_assigned_to_me
              }"
              @dblclick="openEditDialog(bug.id)"
            >
              <!-- Left Column: ID, Status, Content -->
              <div class="flex items-center gap-2 truncate flex-1 mr-3">
                <!-- Bug ID with hover/click flagger -->
                <b
                  class="font-mono font-bold text-gray-800 hover:text-blue-600 px-1 py-0.5 rounded hover:bg-blue-50 cursor-pointer whitespace-nowrap"
                  title="点击切换状态"
                  @click.stop="handleFlaggerClick(bug, $event)"
                >
                  #{{ bug.id }}
                </b>

                <!-- Status Tag with 1-click toggle -->
                <span
                  :class="['status-badge', `status-${bug.status_code}`]"
                  title="点击快捷流转状态"
                  @click.stop="handleQuickStatusToggle(bug)"
                >
                  [{{ bug.status_name }}]
                </span>

                <!-- Content snippet -->
                <span class="truncate text-gray-800">
                  <span v-if="projectStore.currentModuleId === null && bug.module_name" class="text-gray-500 font-medium mr-1">
                    『{{ bug.module_name }}』
                  </span>
                  <span v-html="renderRowSnippet(bug.content)"></span>
                </span>
              </div>

              <!-- Right Column: Attachment, Version, Assignee, Date -->
              <div class="flex items-center gap-3 text-gray-500 text-[11px] whitespace-nowrap">
                <span v-if="bug.has_attachment" title="包含附件" class="text-blue-500">📎</span>
                <span v-if="bug.ver" class="px-1.5 py-0.2 bg-gray-100 text-gray-600 rounded text-[10px]">
                  {{ bug.ver }}
                </span>
                <span
                  class="w-16 text-right truncate"
                  :class="bug.assignee_name === '未指派' ? 'text-gray-400' : 'text-gray-700 font-medium'"
                >
                  {{ bug.assignee_name }}
                </span>
                <span class="text-gray-400 w-12 text-right">{{ formatShortDate(bug.updated_at) }}</span>
              </div>
            </li>
          </ul>

          <div v-else-if="!projectStore.loading" class="py-16 text-center text-gray-400 text-xs">
            木有发现相关 Bug！按 <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded font-mono text-[11px]">Ctrl + `</kbd> 提交新 Bug
          </div>
        </div>

        <!-- Pagination Bar -->
        <div v-if="projectStore.totalPages > 1 || projectStore.totalBugs > 0" class="flex justify-center items-center gap-3 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
          <button
            class="px-2 py-0.5 border border-gray-300 rounded hover:bg-white disabled:opacity-30 transition"
            :disabled="projectStore.page <= 1"
            @click="changePage(projectStore.page - 1)"
          >
            &lt;&lt; 上一页
          </button>
          <span>
            第 <strong>{{ projectStore.page }}</strong> / {{ projectStore.totalPages || 1 }} 页 (共 {{ projectStore.totalBugs }} 条)
          </span>
          <button
            class="px-2 py-0.5 border border-gray-300 rounded hover:bg-white disabled:opacity-30 transition"
            :disabled="projectStore.page >= projectStore.totalPages"
            @click="changePage(projectStore.page + 1)"
          >
            下一页 &gt;&gt;
          </button>
        </div>
      </main>
    </div>

    <!-- Bottom Tips Bar -->
    <footer class="bg-gray-200 border-t border-gray-300 py-1.5 px-4 text-center text-[11px] text-gray-500">
      Tips：<kbd class="font-mono bg-white px-1 py-0.2 border border-gray-300 rounded">Ctrl+`</kbd> 提交新bug；
      <kbd class="font-mono bg-white px-1 py-0.2 border border-gray-300 rounded">Esc</kbd> 关闭弹窗；
      <kbd class="font-mono bg-white px-1 py-0.2 border border-gray-300 rounded">Ctrl+Enter</kbd> 提交bug；
      双击描述查看详情；筛选复选框双击 = 单选；支持截图 <kbd class="font-mono bg-white px-1 py-0.2 border border-gray-300 rounded">Ctrl+V</kbd> 粘贴上传；
    </footer>

    <!-- Flagger Popover -->
    <FlaggerPopover
      :visible="flaggerState.visible"
      :bug-id="flaggerState.bugId"
      :current-status="flaggerState.status"
      :position="flaggerState.position"
      @select="handleFlaggerSelect"
      @close="flaggerState.visible = false"
    />

    <!-- Bug Create / Edit Modal -->
    <BugDialog
      :visible="bugDialogState.visible"
      :bug-id="bugDialogState.bugId"
      @close="bugDialogState.visible = false"
      @saved="handleBugSaved"
      @navigate="handleRollNavigate"
    />

    <!-- Profile & Key Modal -->
    <ProfileModal
      :visible="showProfileModal"
      @close="showProfileModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useProjectStore } from '../stores/project'
import { BugListItem } from '../types'
import { formatShortDate, escapeHtml } from '../utils/formatter'
import FilterBar from '../components/FilterBar.vue'
import FlaggerPopover from '../components/FlaggerPopover.vue'
import BugDialog from '../components/BugDialog.vue'
import ProfileModal from '../components/ProfileModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const showProjectMenu = ref(false)
const showProfileModal = ref(false)

const flaggerState = reactive({
  visible: false,
  bugId: 0,
  status: 1,
  position: { x: 0, y: 0 }
})

const bugDialogState = reactive({
  visible: false,
  bugId: null as number | null
})

function renderRowSnippet(content: string): string {
  if (!content) return ''
  let text = escapeHtml(content)
  text = text.replace(/\[b\](.*?)\[\/b\]/gi, '<strong class="content-bold">$1</strong>')
  return text
}

function handleSelectProject(projectId: number) {
  showProjectMenu.value = false
  projectStore.selectProject(projectId)
}

function openNewBugDialog() {
  bugDialogState.bugId = null
  bugDialogState.visible = true
}

function openEditDialog(bugId: number) {
  bugDialogState.bugId = bugId
  bugDialogState.visible = true
}

function handleFlaggerClick(bug: BugListItem, e: MouseEvent) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  flaggerState.bugId = bug.id
  flaggerState.status = bug.status
  flaggerState.position = { x: rect.left, y: rect.bottom + 4 }
  flaggerState.visible = true
}

async function handleFlaggerSelect(newStatus: number) {
  await projectStore.quickChangeStatus(flaggerState.bugId, newStatus)
}

async function handleQuickStatusToggle(bug: BugListItem) {
  // Toggle: fixed -> closed (0), or new/part_fixed -> fixed (4)
  const nextStatus = bug.status === 4 ? 0 : 4
  await projectStore.quickChangeStatus(bug.id, nextStatus)
}

function handleBugSaved(bugId: number) {
  projectStore.fetchBugs()
  projectStore.fetchProjects()
}

function handleRollNavigate(dir: 'prev' | 'next') {
  if (!bugDialogState.bugId) return
  const idx = projectStore.bugs.findIndex(b => b.id === bugDialogState.bugId)
  if (idx !== -1) {
    if (dir === 'prev' && idx > 0) {
      bugDialogState.bugId = projectStore.bugs[idx - 1].id
    } else if (dir === 'next' && idx < projectStore.bugs.length - 1) {
      bugDialogState.bugId = projectStore.bugs[idx + 1].id
    }
  }
}

function changePage(newPage: number) {
  projectStore.page = newPage
  projectStore.fetchBugs()
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// Global Hotkeys
function handleGlobalKeydown(e: KeyboardEvent) {
  // Ctrl + ` (or Ctrl + ~)
  if (e.ctrlKey && (e.key === '`' || e.keyCode === 192)) {
    e.preventDefault()
    openNewBugDialog()
  }
  // Esc
  if (e.key === 'Escape' || e.keyCode === 27) {
    if (bugDialogState.visible) {
      bugDialogState.visible = false
    }
    if (flaggerState.visible) {
      flaggerState.visible = false
    }
    if (showProfileModal.value) {
      showProfileModal.value = false
    }
    if (showProjectMenu.value) {
      showProjectMenu.value = false
    }
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleGlobalKeydown)
  await projectStore.fetchProjects()
  await projectStore.fetchBugs()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>
