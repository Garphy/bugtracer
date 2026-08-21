import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '../api/client'
import { Project, ProjectDetail, BugListItem, BugListResponse } from '../types'
import { useAuthStore } from './auth'

export const useProjectStore = defineStore('project', () => {
  const authStore = useAuthStore()

  const projects = ref<Project[]>([])
  const currentProjectId = ref<number>(
    parseInt(localStorage.getItem('bt_cur_pid') || '0', 10)
  )
  const currentProjectDetail = ref<ProjectDetail | null>(null)
  const currentModuleId = ref<number | null>(null) // null = all
  const mode = ref<'admin' | 'coder'>(
    (localStorage.getItem('bt_mode') as 'admin' | 'coder') || 'admin'
  )
  const statusFilter = ref<number[]>([1, 2, 3]) // Default: new, key, part_fixed
  const searchQuery = ref<string>('')
  const page = ref<number>(1)
  const pageSize = ref<number>(30)

  const bugs = ref<BugListItem[]>([])
  const totalBugs = ref<number>(0)
  const totalProjectBugs = ref<number>(0)
  const loading = ref<boolean>(false)

  const totalPages = computed(() => Math.ceil(totalBugs.value / pageSize.value) || 1)

  const currentProject = computed(() => {
    return projects.value.find(p => p.id === currentProjectId.value) || projects.value[0] || null
  })

  const totalActiveBugsCount = computed(() => {
    return projects.value.reduce((sum, p) => sum + (p.active_bugs_count || 0), 0)
  })

  async function fetchProjects() {
    try {
      const res = await client.get('/projects')
      projects.value = res.data
      if (projects.value.length > 0) {
        if (!currentProjectId.value || !projects.value.some(p => p.id === currentProjectId.value)) {
          currentProjectId.value = projects.value[0].id
          localStorage.setItem('bt_cur_pid', currentProjectId.value.toString())
        }
        await fetchProjectDetail(currentProjectId.value)
      }
    } catch (e) {
      console.error('Failed to fetch projects', e)
    }
  }

  async function fetchProjectDetail(projectId: number) {
    try {
      const res = await client.get(`/projects/${projectId}`)
      currentProjectDetail.value = res.data
    } catch (e) {
      console.error('Failed to fetch project detail', e)
    }
  }

  async function selectProject(projectId: number) {
    currentProjectId.value = projectId
    localStorage.setItem('bt_cur_pid', projectId.toString())
    currentModuleId.value = null
    page.value = 1
    await fetchProjectDetail(projectId)
    await fetchBugs()
  }

  function selectModule(moduleId: number | null) {
    currentModuleId.value = moduleId
    page.value = 1
    fetchBugs()
  }

  function toggleMode() {
    mode.value = mode.value === 'admin' ? 'coder' : 'admin'
    localStorage.setItem('bt_mode', mode.value)
    page.value = 1
    fetchBugs()
  }

  function setStatusFilter(statuses: number[]) {
    statusFilter.value = statuses
    page.value = 1
    fetchBugs()
  }

  function setSearch(query: string) {
    searchQuery.value = query
    page.value = 1
    fetchBugs()
  }

  async function fetchBugs() {
    if (!currentProjectId.value) return
    loading.value = true
    try {
      const params: any = {
        project_id: currentProjectId.value,
        page: page.value,
        page_size: pageSize.value,
        mode: mode.value,
      }
      if (currentModuleId.value !== null) {
        params.module_id = currentModuleId.value
      }
      if (searchQuery.value.trim()) {
        params.search = searchQuery.value.trim()
      } else {
        params.status = statusFilter.value.join(',')
      }

      const res = await client.get<BugListResponse>('/bugs', { params })
      bugs.value = res.data.items
      totalBugs.value = res.data.total
      totalProjectBugs.value = res.data.counts_summary.total_in_project || res.data.total
    } catch (e) {
      console.error('Failed to fetch bugs', e)
    } finally {
      loading.value = false
    }
  }

  async function quickChangeStatus(bugId: number, status: number) {
    try {
      const res = await client.put(`/bugs/${bugId}/status`, { status })
      const updated = res.data
      const idx = bugs.value.findIndex(b => b.id === bugId)
      if (idx !== -1) {
        bugs.value[idx].status = updated.status
        bugs.value[idx].status_code = updated.status_code
        bugs.value[idx].status_name = updated.status_name
        bugs.value[idx].updated_at = updated.updated_at
      }
      fetchProjects()
      return true
    } catch (e) {
      console.error('Failed to update status', e)
      return false
    }
  }

  return {
    projects,
    currentProjectId,
    currentProject,
    currentProjectDetail,
    currentModuleId,
    mode,
    statusFilter,
    searchQuery,
    page,
    pageSize,
    totalPages,
    bugs,
    totalBugs,
    totalProjectBugs,
    loading,
    totalActiveBugsCount,
    fetchProjects,
    fetchProjectDetail,
    selectProject,
    selectModule,
    toggleMode,
    setStatusFilter,
    setSearch,
    fetchBugs,
    quickChangeStatus
  }
})
