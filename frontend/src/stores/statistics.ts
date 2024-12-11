// src/stores/statistics.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { 
  StudyTimeStats,
  MasteryStats,
  RevisionStats,
  TagStats,
  OverallStats
} from '@/types/statistics'
import { StatisticsAPI } from '@/services/statistics'
import { showToast } from 'vant'
import { statisticsMock } from '@/mock/statistics'

// 控制是否使用mock数据
const USE_MOCK = true

export const useStatisticsStore = defineStore('statistics', () => {
  const studyTimeStats = ref<StudyTimeStats | null>(null)
  const masteryStats = ref<MasteryStats | null>(null)
  const revisionStats = ref<RevisionStats | null>(null)
  const tagStats = ref<TagStats | null>(null)
  const overallStats = ref<OverallStats | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStudyTimeStats({ days = 30 }) {
    try {
      isLoading.value = true
      if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 500)) // 模拟延迟
        studyTimeStats.value = statisticsMock.generateStudyTimeStats(days)
      } else {
        studyTimeStats.value = await StatisticsAPI.getStudyTimeStats({ days })
      }
    } catch (err) {
      error.value = '获取学习时长统计失败'
      showToast('获取学习时长统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMasteryStats() {
    try {
      isLoading.value = true
      if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 500))
        masteryStats.value = statisticsMock.generateMasteryStats()
      } else {
        masteryStats.value = await StatisticsAPI.getMasteryStats()
      }
    } catch (err) {
      error.value = '获取知识点掌握统计失败'
      showToast('获取知识点掌握统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRevisionStats() {
    try {
      isLoading.value = true
      if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 500))
        revisionStats.value = statisticsMock.generateRevisionStats()
      } else {
        revisionStats.value = await StatisticsAPI.getRevisionStats()
      }
    } catch (err) {
      error.value = '获取复习计划统计失败'
      showToast('获取复习计划统计失败')
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTagStats() {
    try {
      isLoading.value = true
      if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 500))
        tagStats.value = statisticsMock.generateTagStats()
      } else {
        tagStats.value = await StatisticsAPI.getTagStats()
      }
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
      if (USE_MOCK) {
        await new Promise(resolve => setTimeout(resolve, 500))
        overallStats.value = statisticsMock.generateOverallStats()
      } else {
        overallStats.value = await StatisticsAPI.getOverallStats()
      }
    } catch (err) {
      error.value = '获取整体统计数据失败'
      showToast('获取整体统计数据失败')
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
        fetchStudyTimeStats({ days: 30 }),
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
    error.value = null
  }

  return {
    studyTimeStats,
    masteryStats,
    revisionStats,
    tagStats,
    overallStats,
    isLoading,
    error,
    fetchStudyTimeStats,
    fetchMasteryStats,
    fetchRevisionStats,
    fetchTagStats,
    fetchOverallStats,
    initializeStatistics,
    clearStatistics
  }
})