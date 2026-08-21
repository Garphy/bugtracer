<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-between text-xs text-gray-800">
    <div>
      <!-- Top Bar -->
      <header class="bg-gray-800 text-gray-200 px-4 py-2.5 flex items-center justify-between border-b border-gray-700 no-print">
        <div class="flex items-center gap-3">
          <router-link to="/" class="text-blue-400 hover:underline font-medium">
            &lt;&lt; [返回Bug列表]
          </router-link>
          <span class="text-gray-400">|</span>
          <span class="text-sm font-bold text-white">项目报告与统计看板</span>
        </div>

        <div class="flex items-center gap-3">
          <!-- Project selector -->
          <select
            v-model="selectedProjectId"
            class="h-7 px-2.5 bg-gray-700 text-white border border-gray-600 rounded text-xs focus:outline-none"
            @change="loadReport"
          >
            <option v-for="p in projectStore.projects" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>

          <button
            class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded font-medium transition"
            @click="exportCsv"
          >
            📥 导出 CSV
          </button>
          <button
            class="bg-gray-600 hover:bg-gray-500 text-white px-3 py-1 rounded font-medium transition"
            @click="printReport"
          >
            🖨️ 打印报告
          </button>
        </div>
      </header>

      <!-- Main Content Container -->
      <main class="max-w-5xl mx-auto my-4 bg-white border border-gray-300 rounded shadow-sm p-6 space-y-6">
        <!-- Project Title Header -->
        <div class="border-b border-gray-200 pb-3 flex justify-between items-center">
          <div>
            <h1 class="text-xl font-bold text-gray-900">{{ reportData?.project_name }} - 全项目质量报告</h1>
            <p class="text-gray-400 text-xs mt-0.5">生成时间：{{ currentTime }}</p>
          </div>
        </div>

        <!-- Section 1: KPI Stats Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-blue-50 border border-blue-200 rounded p-3 text-center">
            <span class="text-gray-500 font-medium">活动 Bug 数量</span>
            <div class="text-2xl font-bold text-blue-600 mt-1">{{ stats?.active_bugs || 0 }}</div>
          </div>
          <div class="bg-green-50 border border-green-200 rounded p-3 text-center">
            <span class="text-gray-500 font-medium">已解决 Bug 数量</span>
            <div class="text-2xl font-bold text-green-600 mt-1">{{ stats?.fixed_bugs || 0 }}</div>
          </div>
          <div class="bg-red-50 border border-red-200 rounded p-3 text-center">
            <span class="text-gray-500 font-medium">高优 / 重要 Bug</span>
            <div class="text-2xl font-bold text-red-600 mt-1">{{ stats?.key_bugs || 0 }}</div>
          </div>
          <div class="bg-gray-50 border border-gray-200 rounded p-3 text-center">
            <span class="text-gray-500 font-medium">项目 Bug 总计</span>
            <div class="text-2xl font-bold text-gray-700 mt-1">{{ stats?.total_bugs || 0 }}</div>
          </div>
        </div>

        <!-- Section 2: Visual Charts (ECharts) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 no-print">
          <!-- 14-Day Trend Chart -->
          <div class="border border-gray-200 rounded p-3 bg-gray-50">
            <h3 class="font-bold text-gray-700 mb-2">近期 Bug 新增 vs 解决趋势 (近14天)</h3>
            <v-chart class="h-56 w-full" :option="trendChartOption" autoresize />
          </div>

          <!-- Status Distribution Chart -->
          <div class="border border-gray-200 rounded p-3 bg-gray-50">
            <h3 class="font-bold text-gray-700 mb-2">缺陷状态分布</h3>
            <v-chart class="h-56 w-full" :option="pieChartOption" autoresize />
          </div>
        </div>

        <!-- Section 3: Member Workload Matrix Table -->
        <div>
          <h2 class="text-sm font-bold text-gray-800 mb-2 pb-1 border-b border-gray-200">
            人员缺陷处理负荷统计表
          </h2>
          <table class="w-full border-collapse border border-gray-300 text-center text-xs">
            <thead>
              <tr class="bg-gray-100 text-gray-700 font-medium">
                <th class="border border-gray-300 py-1.5 px-3">人员姓名</th>
                <th class="border border-gray-300 py-1.5 px-3">活动 Bug (待处理)</th>
                <th class="border border-gray-300 py-1.5 px-3">已解决 Bug</th>
                <th class="border border-gray-300 py-1.5 px-3">重要/高优 Bug</th>
                <th class="border border-gray-300 py-1.5 px-3">累计总指派</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="m in stats?.member_stats || []"
                :key="m.user_id"
                class="hover:bg-gray-50"
              >
                <td class="border border-gray-300 py-1 px-3 font-medium text-left">
                  {{ m.fullname }}
                  <span class="text-gray-400 text-[10px] ml-1">({{ m.role }})</span>
                </td>
                <td class="border border-gray-300 py-1 px-3 font-bold" :class="m.active_count > 0 ? 'text-blue-600' : 'text-gray-400'">
                  {{ m.active_count }}
                </td>
                <td class="border border-gray-300 py-1 px-3 text-green-600 font-medium">{{ m.fixed_count }}</td>
                <td class="border border-gray-300 py-1 px-3 font-bold" :class="m.key_count > 0 ? 'text-red-600' : 'text-gray-400'">
                  {{ m.key_count }}
                </td>
                <td class="border border-gray-300 py-1 px-3 text-gray-700">{{ m.total_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Section 4: Full Bug Items by Module -->
        <div class="space-y-6 pt-4">
          <h2 class="text-base font-bold text-gray-900 pb-2 border-b-2 border-gray-800">
            各模块缺陷详细清单
          </h2>

          <div
            v-for="(bugList, moduleName) in reportData?.bugs_by_module || {}"
            :key="moduleName"
            class="space-y-3"
          >
            <div class="bg-gray-100 px-3 py-1.5 rounded font-bold text-sm text-gray-800 flex justify-between items-center">
              <span>模块：{{ moduleName }}</span>
              <span class="text-xs text-gray-500 font-normal">({{ bugList.length }} 项)</span>
            </div>

            <div class="divide-y divide-gray-200 pl-2">
              <div
                v-for="b in bugList"
                :key="b.id"
                class="py-3 space-y-1.5"
              >
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2">
                    <b class="font-mono font-bold text-blue-700">#{{ b.id }}</b>
                    <span :class="['status-badge', `status-${b.status_code}`]">[{{ b.status_name }}]</span>
                    <span v-if="b.ver" class="text-gray-400 font-mono text-[10px]">[{{ b.ver }}]</span>
                  </div>
                  <div class="text-gray-500 text-[11px]">
                    提交人: {{ b.creator_name }} | 指派: {{ b.assignee_name }} | 更新: {{ formatShortDate(b.updated_at) }}
                  </div>
                </div>

                <div
                  class="text-gray-800 pl-4 py-1 text-xs leading-relaxed break-words"
                  v-html="formatBugContent(b.content)"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-200 border-t border-gray-300 py-2 px-4 text-center text-[11px] text-gray-500 no-print">
      BugTracer 质量分析报告与导出服务
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import { FullProjectReportResponse, ProjectStatsReport } from '../types'
import { formatBugContent, formatShortDate } from '../utils/formatter'
import { useProjectStore } from '../stores/project'
import client from '../api/client'

// Register ECharts modules
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const projectStore = useProjectStore()
const selectedProjectId = ref<number>(projectStore.currentProjectId || 1)
const reportData = ref<FullProjectReportResponse | null>(null)
const currentTime = ref(dayjs().format('YYYY-MM-DD HH:mm:ss'))

const stats = computed<ProjectStatsReport | undefined>(() => reportData.value?.stats)

const trendChartOption = computed(() => {
  const trend = stats.value?.daily_trend || []
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增缺陷', '已解决'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trend.map(t => t.date)
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '新增缺陷',
        type: 'line',
        smooth: true,
        data: trend.map(t => t.created),
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '已解决',
        type: 'line',
        smooth: true,
        data: trend.map(t => t.fixed),
        itemStyle: { color: '#52c41a' }
      }
    ]
  }
})

const pieChartOption = computed(() => {
  const dist = stats.value?.status_distribution || {}
  const data = Object.entries(dist).map(([name, count]) => ({
    name,
    value: count
  }))
  return {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '缺陷状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' }
        },
        data: data
      }
    ]
  }
})

async function loadReport() {
  if (!selectedProjectId.value) return
  try {
    const res = await client.get<FullProjectReportResponse>(`/reports/full/${selectedProjectId.value}`)
    reportData.value = res.data
  } catch (e) {
    console.error('Failed to load full report', e)
  }
}

async function exportCsv() {
  if (!selectedProjectId.value) return
  window.open(`/api/reports/export/${selectedProjectId.value}`, '_blank')
}

function printReport() {
  window.print()
}

onMounted(async () => {
  await projectStore.fetchProjects()
  if (projectStore.currentProjectId) {
    selectedProjectId.value = projectStore.currentProjectId
  }
  loadReport()
})
</script>
