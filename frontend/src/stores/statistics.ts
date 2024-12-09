import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { 
  StudyTimeStats,
  MasteryStats,
  RevisionStats,
  TagStats,
  OverallStats,
  StatsTrend,
  CategoryStats,
  WeeklyReport,
  MonthlyReport 
} from '@/types/statistics'
import { StatisticsAPI } from '@/services/statistics'
import { showToast } from 'vant'

export const useStatisticsStore = defineStore('statistics', () => {
  const studyTimeStats = ref<StudyTimeStats | null>(null)
  const masteryStats = ref<MasteryStats | null>(null)
  const revisionStats = ref<RevisionStats | null>(null)
  const tagStats = ref<TagStats | null>(null)
  const overallStats = ref<OverallStats | null>(null)
  const weeklyReport = ref<WeeklyReport | null>(null)
  const monthlyReport = ref<MonthlyReport | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStudyTimeStats(params: { days?: number } = {}) {
    try {
      isLoading.value = true
      studyTimeStats.value = await StatisticsAPI.getStudyTimeStats(params)
    } catch (err) {
      error.value = '获取学习时长统计失败'
      showToast('获取学习时长统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMasteryStats(params = {}) {
    try {
      isLoading.value = true
      masteryStats.value = await StatisticsAPI.getMasteryStats(params)
    } catch (err) {
      error.value = '获取知识点掌握统计失败'
      showToast('获取知识点掌握统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRevisionStats(params = {}) {
    try {
      isLoading.value = true
      revisionStats.value = await StatisticsAPI.getRevisionStats(params)
    } catch (err) {
      error.value = '获取复习计划统计失败'
      showToast('获取复习计划统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTagStats(params = {}) {
    try {
      isLoading.value = true
      tagStats.value = await StatisticsAPI.getTagStats(params)
    } catch (err) {
      error.value = '获取标签使用统计失败'
      showToast('获取标签使用统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchOverallStats() {
    try {
      isLoading.value = true
      overallStats.value = await StatisticsAPI.getOverallStats()
    } catch (err) {
      error.value = '获取整体统计数据失败'
      showToast('获取整体统计数据失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchWeeklyReport(params = {}) {
    try {
      isLoading.value = true
      weeklyReport.value = await StatisticsAPI.getWeeklyReport(params)
    } catch (err) {
      error.value = '获取周报失败'
      showToast('获取周报失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMonthlyReport(params = {}) {
    try {
      isLoading.value = true
      monthlyReport.value = await StatisticsAPI.getMonthlyReport(params)
    } catch (err) {
      error.value = '获取月报失败'
      showToast('获取月报失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function initializeStatistics() {
    try {
      isLoading.value = true
      await Promise.all([
        fetchOverallStats(),
        fetchStudyTimeStats(),
        fetchMasteryStats(),
        fetchRevisionStats(),
        fetchTagStats()
      ])
    } catch (err) {
      error.value = '初始化统计数据失败'
      showToast('初始化统计数据失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  function clearStatistics() {
    studyTimeStats.value = null
    masteryStats.value = null
    revisionStats.value = null
    tagStats.value = null
    overallStats.value = null
    weeklyReport.value = null
    monthlyReport.value = null
    error.value = null
  }

  return {
    studyTimeStats,
    masteryStats,
    revisionStats,
    tagStats,
    overallStats,
    weeklyReport,
    monthlyReport,
    isLoading,
    error,
    fetchStudyTimeStats,
    fetchMasteryStats,
    fetchRevisionStats,
    fetchTagStats,
    fetchOverallStats,
    fetchWeeklyReport,
    fetchMonthlyReport,
    initializeStatistics,
    clearStatistics
  }
}) 