<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-between text-xs text-gray-700">
    <div>
      <!-- Top Bar -->
      <header class="bg-gray-800 text-gray-200 px-4 py-2.5 flex items-center justify-between border-b border-gray-700">
        <h1 class="text-sm font-bold text-white flex items-center gap-2">
          <span>BugTracer 管理后台</span>
        </h1>
        <router-link to="/" class="text-blue-400 hover:underline flex items-center gap-1">
          &lt;&lt; [返回前台主页]
        </router-link>
      </header>

      <main class="max-w-4xl mx-auto my-4 bg-white border border-gray-300 rounded shadow-sm overflow-hidden">
        <!-- Sub Navigation Tabs -->
        <div class="bg-gray-100 border-b border-gray-300 px-4 flex items-center gap-2">
          <button
            class="px-4 py-2.5 font-medium border-b-2 transition"
            :class="activeTab === 'projects' ? 'border-blue-600 text-blue-600 bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
            @click="switchTab('projects')"
          >
            项目管理
          </button>
          <button
            class="px-4 py-2.5 font-medium border-b-2 transition"
            :class="activeTab === 'members' ? 'border-blue-600 text-blue-600 bg-white' : 'border-transparent text-gray-600 hover:text-gray-900'"
            @click="switchTab('members')"
          >
            人员管理
          </button>
        </div>

        <div class="p-5">
          <!-- ================= Projects Tab ================= -->
          <div v-if="activeTab === 'projects'">
            <!-- Project List View -->
            <div v-if="!editingProject">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-sm font-bold text-gray-800">所有项目列表</h2>
                <button
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded font-medium transition"
                  @click="openNewProject"
                >
                  + 新建项目
                </button>
              </div>

              <div class="space-y-3">
                <div
                  v-for="p in projects"
                  :key="p.id"
                  class="border border-gray-200 rounded p-3 bg-gray-50 flex items-start justify-between"
                >
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="font-mono text-gray-400 font-bold">#{{ p.id }}</span>
                      <strong class="text-sm text-gray-800">{{ p.name }}</strong>
                      <span v-if="p.default_version" class="bg-gray-200 text-gray-600 text-[10px] px-1.5 py-0.2 rounded">
                        默认版本: {{ p.default_version }}
                      </span>
                    </div>
                    <p v-if="p.description" class="text-gray-500 mt-1 text-[11px]">{{ p.description }}</p>
                  </div>

                  <div class="flex items-center gap-2">
                    <button class="text-blue-600 hover:underline font-medium" @click="editProject(p.id)">[编辑项目/模块]</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Project Edit / Create Form -->
            <div v-else class="max-w-xl">
              <div class="flex items-center justify-between mb-3 pb-2 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800">{{ isNewProject ? '新建项目' : `编辑项目: ${projectForm.name}` }}</h2>
                <button class="text-gray-500 hover:underline" @click="editingProject = false">&lt;&lt; 返回项目列表</button>
              </div>

              <div class="space-y-3">
                <div>
                  <label class="block font-medium text-gray-700 mb-1">项目名称：</label>
                  <input
                    v-model="projectForm.name"
                    type="text"
                    class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    placeholder="如: 商城前台系统"
                  />
                </div>

                <div>
                  <label class="block font-medium text-gray-700 mb-1">默认版本号：</label>
                  <input
                    v-model="projectForm.default_version"
                    type="text"
                    class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    placeholder="如: v1.0.0"
                  />
                </div>

                <!-- Sub Modules list -->
                <div>
                  <div class="flex justify-between items-center mb-1">
                    <label class="block font-medium text-gray-700">子分类 / 模块清单：</label>
                    <button class="text-blue-600 hover:underline text-xs" @click="addModuleItem">[+ 增加子模块]</button>
                  </div>
                  <ul class="space-y-1.5 bg-gray-50 p-2.5 border border-gray-200 rounded">
                    <li
                      v-for="(mod, idx) in projectForm.modules"
                      :key="idx"
                      class="flex items-center gap-2"
                    >
                      <input
                        v-model="mod.name"
                        type="text"
                        placeholder="模块名称 (如 用户中心, 支付网关)"
                        class="flex-1 px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:border-blue-500 bg-white"
                      />
                      <button
                        class="text-red-500 hover:text-red-700 font-bold px-1"
                        title="删除该分类"
                        @click="removeModuleItem(idx)"
                      >
                        ✕
                      </button>
                    </li>
                  </ul>
                </div>

                <!-- Member Assignment -->
                <div>
                  <label class="block font-medium text-gray-700 mb-1">分配指派技术成员：</label>
                  <div class="grid grid-cols-3 gap-2 bg-gray-50 p-2.5 border border-gray-200 rounded max-h-40 overflow-y-auto">
                    <label
                      v-for="u in members"
                      :key="u.id"
                      class="flex items-center gap-1.5 cursor-pointer select-none"
                    >
                      <input
                        type="checkbox"
                        :value="u.id"
                        :checked="projectForm.member_ids.includes(u.id)"
                        class="rounded border-gray-300 text-blue-600"
                        @change="toggleProjectMember(u.id)"
                      />
                      <span>{{ u.fullname }} <span class="text-gray-400 text-[10px]">({{ u.role }})</span></span>
                    </label>
                  </div>
                </div>

                <div v-if="projectError" class="text-red-500 font-medium">{{ projectError }}</div>

                <div class="pt-3 border-t border-gray-200 flex gap-2">
                  <button
                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded font-medium transition"
                    @click="saveProject"
                  >
                    保存项目
                  </button>
                  <button
                    class="border border-gray-300 hover:bg-gray-100 text-gray-700 px-3 py-1.5 rounded font-medium transition"
                    @click="editingProject = false"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ================= Members Tab ================= -->
          <div v-else-if="activeTab === 'members'">
            <!-- Members List View -->
            <div v-if="!editingMember">
              <div class="flex justify-between items-center mb-4">
                <h2 class="text-sm font-bold text-gray-800">团队人员列表</h2>
                <button
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded font-medium transition"
                  @click="openNewMember"
                >
                  + 新增人员
                </button>
              </div>

              <!-- Grouped by Role -->
              <div class="space-y-4">
                <div v-for="role in ['admin', 'coder', 'tester', 'guest']" :key="role">
                  <div class="font-bold text-gray-500 uppercase tracking-wider text-[11px] mb-1.5 pb-1 border-b border-gray-200">
                    {{ getRoleTitle(role) }}
                  </div>
                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    <div
                      v-for="u in membersByRole(role)"
                      :key="u.id"
                      class="border border-gray-200 rounded p-2 bg-gray-50 flex items-center justify-between"
                    >
                      <div>
                        <span class="font-bold text-gray-800">{{ u.fullname }}</span>
                        <span class="text-gray-400 text-[11px] ml-1">({{ u.username }})</span>
                      </div>
                      <button class="text-blue-600 hover:underline font-medium" @click="editMember(u)">[修改]</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Member Edit / Create Form -->
            <div v-else class="max-w-md">
              <div class="flex items-center justify-between mb-3 pb-2 border-b border-gray-200">
                <h2 class="text-sm font-bold text-gray-800">{{ isNewMember ? '新增人员' : `修改人员: ${memberForm.fullname}` }}</h2>
                <button class="text-gray-500 hover:underline" @click="editingMember = false">&lt;&lt; 返回人员列表</button>
              </div>

              <div class="space-y-3">
                <div>
                  <label class="block font-medium text-gray-700 mb-1">真实姓名 / 昵称：</label>
                  <input
                    v-model="memberForm.fullname"
                    type="text"
                    class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    placeholder="如: 张三"
                  />
                </div>

                <div>
                  <label class="block font-medium text-gray-700 mb-1">登录账号 (仅限英文字母与数字)：</label>
                  <input
                    v-model="memberForm.username"
                    type="text"
                    class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    placeholder="如: zhangsan"
                  />
                </div>

                <div>
                  <label class="block font-medium text-gray-700 mb-1">系统权限角色：</label>
                  <div class="flex gap-4">
                    <label class="flex items-center gap-1 cursor-pointer">
                      <input v-model="memberForm.role" type="radio" value="admin" class="text-blue-600" />
                      <span>管理员 (admin)</span>
                    </label>
                    <label class="flex items-center gap-1 cursor-pointer">
                      <input v-model="memberForm.role" type="radio" value="coder" class="text-blue-600" />
                      <span>技术开发 (coder)</span>
                    </label>
                    <label class="flex items-center gap-1 cursor-pointer">
                      <input v-model="memberForm.role" type="radio" value="tester" class="text-blue-600" />
                      <span>测试人员 (tester)</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label class="block font-medium text-gray-700 mb-1">
                    {{ isNewMember ? '初始登录密码 (默认 123456)：' : '重置密码 (留空则不修改)：' }}
                  </label>
                  <input
                    v-model="memberForm.password"
                    type="password"
                    class="w-full px-2.5 py-1.5 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    placeholder="请输入密码"
                  />
                </div>

                <div v-if="memberError" class="text-red-500 font-medium">{{ memberError }}</div>

                <div class="pt-3 border-t border-gray-200 flex gap-2">
                  <button
                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded font-medium transition"
                    @click="saveMember"
                  >
                    保存人员
                  </button>
                  <button
                    class="border border-gray-300 hover:bg-gray-100 text-gray-700 px-3 py-1.5 rounded font-medium transition"
                    @click="editingMember = false"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Tips Footer -->
    <footer class="bg-gray-200 border-t border-gray-300 py-1.5 px-4 text-center text-[11px] text-gray-500">
      BugTracer 后台管理：项目管理与人员权限统一配置
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Project, ProjectDetail, User } from '../types'
import client from '../api/client'

const activeTab = ref<'projects' | 'members'>('projects')

// Projects State
const projects = ref<Project[]>([])
const editingProject = ref(false)
const isNewProject = ref(false)
const currentEditProjectId = ref<number | null>(null)
const projectError = ref('')

const projectForm = reactive({
  name: '',
  description: '',
  default_version: '',
  modules: [] as Array<{ id?: number; name: string }>,
  member_ids: [] as number[]
})

// Members State
const members = ref<User[]>([])
const editingMember = ref(false)
const isNewMember = ref(false)
const currentEditUserId = ref<number | null>(null)
const memberError = ref('')

const memberForm = reactive({
  username: '',
  fullname: '',
  role: 'coder' as 'admin' | 'coder' | 'tester' | 'guest',
  password: ''
})

function switchTab(tab: 'projects' | 'members') {
  activeTab.value = tab
  editingProject.value = false
  editingMember.value = false
}

function getRoleTitle(role: string) {
  switch (role) {
    case 'admin': return '系统管理员 (Admin)'
    case 'coder': return '技术开发人员 (Coder)'
    case 'tester': return '测试质量人员 (Tester)'
    case 'guest': return '访客人员 (Guest)'
    default: return role
  }
}

function membersByRole(role: string) {
  return members.value.filter(u => u.role === role)
}

// Project Operations
async function fetchProjects() {
  try {
    const res = await client.get('/projects')
    projects.value = res.data
  } catch (e) {}
}

async function openNewProject() {
  isNewProject.value = true
  currentEditProjectId.value = null
  projectForm.name = ''
  projectForm.description = ''
  projectForm.default_version = ''
  projectForm.modules = [{ name: '默认模块' }]
  projectForm.member_ids = []
  projectError.value = ''
  editingProject.value = true
}

async function editProject(projectId: number) {
  isNewProject.value = false
  currentEditProjectId.value = projectId
  projectError.value = ''
  try {
    const res = await client.get<ProjectDetail>(`/projects/${projectId}`)
    const p = res.data
    projectForm.name = p.name
    projectForm.description = p.description
    projectForm.default_version = p.default_version
    projectForm.modules = p.modules.map(m => ({ id: m.id, name: m.name }))
    projectForm.member_ids = p.members.map(m => m.id)
    editingProject.value = true
  } catch (e) {}
}

function addModuleItem() {
  projectForm.modules.push({ name: '' })
}

function removeModuleItem(index: number) {
  projectForm.modules.splice(index, 1)
}

function toggleProjectMember(userId: number) {
  if (projectForm.member_ids.includes(userId)) {
    projectForm.member_ids = projectForm.member_ids.filter(id => id !== userId)
  } else {
    projectForm.member_ids.push(userId)
  }
}

async function saveProject() {
  if (!projectForm.name.trim()) {
    projectError.value = '项目名称不能为空'
    return
  }
  projectError.value = ''
  try {
    const moduleNames = projectForm.modules.map(m => m.name.trim()).filter(n => !!n)
    if (isNewProject.value) {
      await client.post('/projects', {
        name: projectForm.name.trim(),
        description: projectForm.description,
        default_version: projectForm.default_version,
        modules: moduleNames,
        member_ids: projectForm.member_ids
      })
    } else if (currentEditProjectId.value) {
      await client.put(`/projects/${currentEditProjectId.value}`, {
        name: projectForm.name.trim(),
        description: projectForm.description,
        default_version: projectForm.default_version,
        member_ids: projectForm.member_ids
      })
      // Sync modules
      for (const m of projectForm.modules) {
        if (m.name.trim()) {
          if (m.id) {
            await client.put(`/projects/modules/${m.id}`, { name: m.name.trim() })
          } else {
            await client.post(`/projects/${currentEditProjectId.value}/modules`, { name: m.name.trim(), sort_order: 0 })
          }
        }
      }
    }
    await fetchProjects()
    editingProject.value = false
  } catch (e: any) {
    projectError.value = e.response?.data?.detail || '保存项目失败'
  }
}

// Member Operations
async function fetchMembers() {
  try {
    const res = await client.get('/auth/users/all')
    members.value = res.data
  } catch (e) {}
}

function openNewMember() {
  isNewMember.value = true
  currentEditUserId.value = null
  memberForm.username = ''
  memberForm.fullname = ''
  memberForm.role = 'coder'
  memberForm.password = ''
  memberError.value = ''
  editingMember.value = true
}

function editMember(user: User) {
  isNewMember.value = false
  currentEditUserId.value = user.id
  memberForm.username = user.username
  memberForm.fullname = user.fullname
  memberForm.role = user.role
  memberForm.password = ''
  memberError.value = ''
  editingMember.value = true
}

async function saveMember() {
  if (!memberForm.username.trim()) {
    memberError.value = '登录账号不能为空'
    return
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(memberForm.username.trim())) {
    memberError.value = '账号请使用英文字母与数字'
    return
  }
  memberError.value = ''
  try {
    if (isNewMember.value) {
      await client.post('/auth/users', {
        username: memberForm.username.trim(),
        fullname: memberForm.fullname.trim() || memberForm.username.trim(),
        role: memberForm.role,
        password: memberForm.password || '123456'
      })
    } else if (currentEditUserId.value) {
      const payload: any = {
        username: memberForm.username.trim(),
        fullname: memberForm.fullname.trim(),
        role: memberForm.role
      }
      if (memberForm.password) {
        payload.password = memberForm.password
      }
      await client.put(`/auth/users/${currentEditUserId.value}`, payload)
    }
    await fetchMembers()
    editingMember.value = false
  } catch (e: any) {
    memberError.value = e.response?.data?.detail || '保存人员失败'
  }
}

onMounted(() => {
  fetchProjects()
  fetchMembers()
})
</script>
