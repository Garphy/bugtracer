<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-between">
    <!-- Top Toast Notification -->
    <div
      v-if="toast.visible"
      class="fixed top-3 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded shadow-lg text-xs font-medium transition-all duration-200 animate-in fade-in slide-in-from-top-2 flex items-center gap-2"
      :class="toast.type === 'error' ? 'bg-red-600 text-white' : (toast.type === 'warn' ? 'bg-amber-500 text-white' : 'bg-gray-900 text-white')"
    >
      <span>{{ toast.message }}</span>
    </div>

    <!-- Top Header Bar -->
    <div>
      <header class="bg-gray-800 text-gray-200 px-4 py-2 flex flex-wrap items-center justify-between text-xs border-b border-gray-700">
        <!-- Left: Login user & Mode -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-gray-400">登录身份:</span>
            <strong class="text-white">{{ authStore.user?.fullname }} ({{ authStore.user?.username }})</strong>
            <span class="bg-gray-700 text-gray-300 text-[10px] px-1.5 py-0.2 rounded uppercase font-mono">{{ authStore.user?.role }}</span>
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

          <!-- Action Buttons: + Submit Bug & Copy List -->
          <div class="flex items-center gap-1.5 my-1">
            <button
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium flex items-center gap-1 transition shadow-sm"
              title="快捷键：Ctrl + `"
              @click="openNewBugDialog"
            >
              <span>+ 提交新 Bug</span>
              <kbd class="hidden sm:inline text-[10px] bg-blue-700 px-1 rounded">^`</kbd>
            </button>

            <button
              class="bg-white hover:bg-gray-50 text-gray-700 hover:text-blue-600 border border-gray-300 px-2 py-1 rounded text-xs font-medium flex items-center gap-1 transition shadow-sm"
              title="复制当前页面 Bug 列表到剪贴板"
              @click="copyBugList"
            >
              <Copy class="w-3.5 h-3.5" />
              <span>复制列表</span>
            </button>
          </div>
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
              <div class="flex items-center gap-1.5 truncate flex-1 mr-3">
                <!-- Bug ID with hover icon indicator (# -> ChevronDown) -->
                <b
                  class="group/id font-mono font-bold text-gray-800 hover:text-blue-600 px-1 py-0.5 rounded hover:bg-blue-50 cursor-pointer whitespace-nowrap min-w-[46px] inline-flex items-center gap-0.5 text-left tabular-nums transition"
                  title="点击弹出状态流转菜单"
                  @click.stop="handleFlaggerClick(bug, $event)"
                >
                  <span class="text-gray-400 group-hover/id:hidden">#</span>
                  <ChevronDown class="w-3 h-3 text-blue-600 hidden group-hover/id:inline-block animate-in fade-in" />
                  <span>{{ bug.id }}</span>
                </b>

                <!-- Status Tag with tick hover preview effect -->
                <span
                  :class="['status-badge group/status', `status-${bug.status_code}`, 'w-[64px] text-center inline-flex items-center justify-center flex-shrink-0 relative overflow-hidden']"
                  :title="getStatusClickTitle(bug)"
                  @click.stop="handleQuickStatusToggle(bug)"
                >
                  <span class="group-hover/status:hidden">[{{ bug.status_name }}]</span>
                  <span v-if="[1, 2, 3].includes(bug.status)" class="hidden group-hover/status:inline-block text-green-700 font-bold bg-green-100/90 px-1 rounded text-[10px]">
                    ✓ 解决
                  </span>
                  <span v-else-if="bug.status === 4 && (authStore.isAdmin || authStore.isTester)" class="hidden group-hover/status:inline-block text-gray-700 font-bold bg-gray-200/90 px-1 rounded text-[10px]">
                    ✓ 关闭
                  </span>
                  <span v-else-if="bug.status === 0 && (authStore.isAdmin || authStore.isTester)" class="hidden group-hover/status:inline-block text-blue-700 font-bold bg-blue-100/90 px-1 rounded text-[10px]">
                    ↺ 激活
                  </span>
                  <span v-else class="hidden group-hover/status:inline-block">
                    [{{ bug.status_name }}]
                  </span>
                </span>

                <!-- Content snippet -->
                <span class="truncate text-gray-800 pl-1">
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

          <div v-else-if="!projectStore.loading" class="py-16 text-center text-gray-400 text-xs space-y-2">
            <div class="text-gray-500 font-medium">当前筛选条件下未发现 Bug</div>
            <div class="text-[11px] text-gray-400">
              可尝试点击 <button class="text-blue-600 hover:underline font-medium" @click="projectStore.setStatusFilter([0,1,2,3,4,5,6,7])">【全选状态】</button> 或按 <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded font-mono text-[11px]">Ctrl + `</kbd> 提交新 Bug
            </div>
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
      点击状态标签一键流转；双击描述查看详情；筛选复选框双击 = 单选；支持截图 <kbd class="font-mono bg-white px-1 py-0.2 border border-gray-300 rounded">Ctrl+V</kbd> 粘贴上传；
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
import { ChevronDown, Copy } from 'lucide-vue-next'
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

const toast = reactive({
  visible: false,
  message: '',
  type: 'info' as 'info' | 'warn' | 'error'
})
let toastTimer: any = null

function showToast(message: string, type: 'info' | 'warn' | 'error' = 'info') {
  clearTimeout(toastTimer)
  toast.message = message
  toast.type = type
  toast.visible = true
  toastTimer = setTimeout(() => {
    toast.visible = false
  }, 2500)
}

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
  const success = await projectStore.quickChangeStatus(flaggerState.bugId, newStatus)
  if (success) {
    showToast(`Bug #${flaggerState.bugId} 状态已更新`, 'info')
  }
}

function getStatusClickTitle(bug: BugListItem): string {
  const role = authStore.user?.role
  if ([1, 2, 3].includes(bug.status)) {
    return '点击快捷标记为：已解决(fixed)'
  } else if (bug.status === 4) {
    if (role === 'admin' || role === 'tester') {
      return '点击确认验收并标记为：已关闭(closed)'
    } else {
      return '技术开发角色无法直接关闭，需由测试/管理员验收关闭'
    }
  } else if (bug.status === 0) {
    if (role === 'admin' || role === 'tester') {
      return '点击重新激活为：新增(new)'
    }
  }
  return '点击 Bug ID 弹出完整状态菜单'
}

async function handleQuickStatusToggle(bug: BugListItem) {
  const role = authStore.user?.role

  // 1. If currently active (new=1, key=2, part_fixed=3) -> Quick set to fixed (4)
  if ([1, 2, 3].includes(bug.status)) {
    const success = await projectStore.quickChangeStatus(bug.id, 4)
    if (success) {
      showToast(`Bug #${bug.id} 已快捷标记为 [已解决]`, 'info')
    }
    return
  }

  // 2. If currently fixed (4)
  if (bug.status === 4) {
    if (role === 'admin' || role === 'tester') {
      const success = await projectStore.quickChangeStatus(bug.id, 0)
      if (success) {
        showToast(`Bug #${bug.id} 验收通过，已快捷标记为 [已关闭]`, 'info')
      }
    } else {
      showToast(`技术开发角色无法直接关闭缺陷，请由测试人员或管理员验收后关闭。`, 'warn')
    }
    return
  }

  // 3. If currently closed (0)
  if (bug.status === 0) {
    if (role === 'admin' || role === 'tester') {
      const success = await projectStore.quickChangeStatus(bug.id, 1)
      if (success) {
        showToast(`Bug #${bug.id} 已重新激活为 [新增]`, 'info')
      }
    } else {
      showToast(`技术开发角色无法直接重新激活已关闭的缺陷。`, 'warn')
    }
    return
  }

  // Other statuses: hint user to use Flagger menu
  showToast(`请点击 Bug ID (#${bug.id}) 弹出菜单选择目标状态`, 'info')
}

// Copy current page bugs to clipboard
async function copyBugList() {
  if (projectStore.bugs.length === 0) {
    showToast('当前列表无缺陷可复制', 'warn')
    return
  }
  const lines = projectStore.bugs.map(b => {
    const mod = b.module_name && b.module_name !== '全部' ? `『${b.module_name}』` : ''
    const ver = b.ver ? ` [${b.ver}]` : ''
    const assignee = b.assignee_name && b.assignee_name !== '未指派' ? ` (指派: ${b.assignee_name})` : ''
    // Strip [b] and HTML for clean text
    const cleanContent = b.content.replace(/\[\/?b\]/gi, '').replace(/<[^>]+>/g, '').trim()
    return `#${b.id} [${b.status_name}]${ver} ${mod}${cleanContent}${assignee}`
  })
  const textToCopy = lines.join('\n')

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textToCopy)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = textToCopy
      textarea.style.position = 'fixed'
      textarea.style.left = '-999999px'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    showToast(`已复制当前页 ${lines.length} 条缺陷到剪贴板！`, 'info')
  } catch (err) {
    showToast('复制到剪贴板失败，请手动复制', 'error')
  }
}

function handleBugSaved(bugId: number) {
  projectStore.fetchBugs()
  projectStore.fetchProjects()
  showToast(`Bug 保存成功！`, 'info')
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
  clearTimeout(toastTimer)
})
</script>
