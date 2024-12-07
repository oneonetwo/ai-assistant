import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { RevisionAPI } from '@/services/revisionService'
import type { RevisionPlan, RevisionTask, RevisionStatus, RevisionHistory, RevisionSummary } from '@/types/revision'
import { showToast } from 'vant'

interface FetchPlansParams {
  status?: string
}

interface GetPlanTasksParams {
  date?: string
  status?: 'pending' | 'completed' | 'skipped'
}

export const useRevisionStore = defineStore('revision', () => {
  // 状态
  const plans = ref<RevisionPlan[]>([])
  const currentPlan = ref<RevisionPlan | null>(null)
  const dailyTasks = ref<RevisionTask[]>([])
  const planTasks = ref<RevisionTask[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const reviewHistory = ref<RevisionHistory[]>([])
  const dailySummary = ref<RevisionSummary | null>(null)

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

  async function updateTaskStatus(taskId: number, masteryLevel: RevisionTask['mastery_level']) {
    try {
      const updatedTask = await RevisionAPI.updateTaskStatus(taskId, masteryLevel)
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

  async function fetchPlanTasks(planId: number, params: GetPlanTasksParams = {}) {
    try {
      isLoading.value = true
      const tasks = await RevisionAPI.getPlanTasks(planId, params)
      planTasks.value = tasks
      return tasks
    } catch (err) {
      error.value = '获取计划任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    plans.value = []
    currentPlan.value = null
    dailyTasks.value = []
    planTasks.value = []
    isLoading.value = false
    error.value = null
  }

  async function getNextTask(params: { 
    plan_id?: number
    mode?: 'normal' | 'quick' 
  }) {
    try {
      isLoading.value = true
      return await RevisionAPI.getNextTask(params)
    } catch (err) {
      error.value = '获取下一个任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function batchUpdateTasks(data: {
    task_ids: number[]
    status: 'completed' | 'skipped'
    mastery_level: RevisionTask['mastery_level']
    revision_mode: 'normal' | 'quick'
    time_spent?: number
    comments?: string
  }) {
    try {
      const updatedTasks = await RevisionAPI.batchUpdateTaskStatus(data)
      // 更新本地状态
      updatedTasks.forEach(task => {
        const index = dailyTasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) {
          dailyTasks.value[index] = task
        }
      })
      return updatedTasks
    } catch (err) {
      error.value = '批量更新任务失败'
      throw err
    }
  }

  async function getTaskHistory(taskId: number) {
    try {
      isLoading.value = true
      reviewHistory.value = await RevisionAPI.getTaskHistory(taskId)
      return reviewHistory.value
    } catch (err) {
      error.value = '获取任务历史失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function adjustTaskSchedule(data: {
    task_id: number
    new_date: string
    priority?: number
    comments?: string
  }) {
    try {
      return await RevisionAPI.adjustTaskSchedule(data)
    } catch (err) {
      error.value = '调整任务计划失败'
      throw err
    }
  }

  async function fetchDailySummary(date?: string) {
    try {
      isLoading.value = true
      dailySummary.value = await RevisionAPI.getDailySummary(date)
      return dailySummary.value
    } catch (err) {
      error.value = '获取每日统计失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 检查手册的复习计划
  async function checkHandbookPlans(handbookId: number) {
    try {
      isLoading.value = true
      return await RevisionAPI.checkHandbookPlans(handbookId)
    } catch (err) {
      error.value = '获取手册复习计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 添加笔记到复习计划
  async function addNoteToPlan(planId: number, data: {
    note_id: number
    start_date: string
    priority: number
  }) {
    try {
      isLoading.value = true
      await RevisionAPI.addNoteToPlan(planId, data)
      showToast('添加成功')
    } catch (err) {
      error.value = '添加到复习计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 批量添加笔记到多个复习计划
   */
  async function addNoteToPlansBatch(data: {
    note_id: number
    plan_ids: number[]
    start_date?: string
    priority?: number
  }) {
    try {
      isLoading.value = true
      const result = await RevisionAPI.addNoteToPlansBatch(data)
      
      // 显示操作结果
      // const successCount = result.details.filter(d => d.status === 'success').length
      // const skippedCount = result.details.filter(d => d.status === 'skipped').length
      
      showToast(`添加成功`)
      
      return result
    } catch (err) {
      error.value = '批量添加到复习计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // 状态
    plans,
    currentPlan,
    dailyTasks,
    planTasks,
    isLoading,
    error,
    reviewHistory,
    dailySummary,
    
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
    fetchPlanTasks,
    reset,
    getNextTask,
    batchUpdateTasks,
    getTaskHistory,
    adjustTaskSchedule,
    fetchDailySummary,
    checkHandbookPlans,
    addNoteToPlan,
    addNoteToPlansBatch
  }
}) 