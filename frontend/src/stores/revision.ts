import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { RevisionAPI } from '@/services/revisionService'
import type { RevisionPlan, RevisionTask, RevisionStatus } from '@/types/revision'
import { showToast } from 'vant'

interface FetchPlansParams {
  status?: string
}

export const useRevisionStore = defineStore('revision', () => {
  // 状态
  const plans = ref<RevisionPlan[]>([])
  const currentPlan = ref<RevisionPlan | null>(null)
  const dailyTasks = ref<RevisionTask[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const completedTasksCount = computed(() => 
    dailyTasks.value.filter(task => task.status === 'mastered').length
  )

  const totalTasksCount = computed(() => dailyTasks.value.length)

  const progress = computed(() => 
    totalTasksCount.value ? 
    Math.round((completedTasksCount.value / totalTasksCount.value) * 100) : 0
  )

  // 方法
  async function fetchPlans(params: FetchPlansParams = {}) {
    isLoading.value = true
    try {
      const response = await RevisionAPI.getPlans(params)
      plans.value = response
    } finally {
      isLoading.value = false
    }
  }

  async function createPlan(planData: {
    name: string
    start_date: string
    end_date: string
    handbook_ids: number[]
    category_ids?: number[]
    tag_ids?: number[]
    note_statuses?: string[]
  }) {
    try {
      isLoading.value = true
      const plan = await RevisionAPI.createPlan(planData)
      plans.value.unshift(plan)
      return plan
    } catch (err) {
      error.value = '创建复习计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPlan(planId: number) {
    try {
      isLoading.value = true
      const plan = await RevisionAPI.getPlan(planId)
      currentPlan.value = plan
      return plan
    } catch (err) {
      error.value = '获取计划详情失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDailyTasks() {
    try {
      isLoading.value = true
      const tasks = await RevisionAPI.getDailyTasks()
      dailyTasks.value = tasks
    } catch (err) {
      error.value = '获取每日任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateTaskStatus(taskId: number, status: RevisionTask['status']) {
    try {
      const updatedTask = await RevisionAPI.updateTaskStatus(taskId, status)
      const index = dailyTasks.value.findIndex(task => task.id === taskId)
      if (index !== -1) {
        dailyTasks.value[index] = updatedTask
      }
      showToast('更新成功')
    } catch (err) {
      error.value = '更新任务状态失败'
      throw err
    }
  }

  function reset() {
    plans.value = []
    currentPlan.value = null
    dailyTasks.value = []
    isLoading.value = false
    error.value = null
  }

  return {
    // 状态
    plans,
    currentPlan,
    dailyTasks,
    isLoading,
    error,
    
    // 计算属性
    completedTasksCount,
    totalTasksCount,
    progress,
    
    // 方法
    fetchPlans,
    createPlan,
    fetchPlan,
    fetchDailyTasks,
    updateTaskStatus,
    reset
  }
}) 