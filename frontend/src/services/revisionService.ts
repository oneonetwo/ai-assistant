import { request } from '@/utils/request'
import type { RevisionPlan, RevisionTask, RevisionHistory, RevisionSummary } from '@/types/revision'

const API_BASE_URL = '/api/v1/revisions'

interface GetPlanTasksParams {
  date?: string
  status?: 'pending' | 'completed' | 'skipped'
}

interface AddNoteToPlansBatchResult {
  success: boolean
  message: string
  details: {
    plan_id: number
    status: 'success' | 'skipped' | 'failed'
    message?: string
  }[]
}

interface GetDailyTasksParams {
  date?: string
  status?: 'pending' | 'completed' | 'skipped'
}

export class RevisionAPI {
  // 创建复习计划
  static async createPlan(data: {
    name: string
    start_date: string
    end_date: string
    handbook_ids: number[]
    category_ids?: number[]
    tag_ids?: number[]
    note_statuses?: string[]
  }): Promise<RevisionPlan> {
    const response = await request.post(`${API_BASE_URL}/plans`, data)
    return response
  }

  // 获取计划列表
  static async getPlans(params: GetPlansParams = {}): Promise<RevisionPlan[]> {
    const response = await request.get(`${API_BASE_URL}/plans`, { params })
    return response
  }


  // 获取计划详情
  static async getPlan(planId: number): Promise<RevisionPlan> {
    const response = await request.get(`${API_BASE_URL}/plans/${planId}`)
    return response
  }

  // 获取计划任务列表
  static async getPlanTasks(
    planId: number, 
    params: GetPlanTasksParams = {}
  ): Promise<RevisionTask[]> {
    const response = await request.get(`${API_BASE_URL}/plans/${planId}/tasks`, {
      params
    })
    return response
  }

  // 更新任务状态
  static async updateTaskStatus(
    taskId: number,
    masteryLevel: RevisionTask['mastery_level']
  ): Promise<RevisionTask> {
    const response = await request.patch(`${API_BASE_URL}/tasks/${taskId}`, {
      mastery_level: masteryLevel
    })
    return response
  }

  // 获取每日任务
  static async getDailyTasks(params: GetDailyTasksParams = {}): Promise<RevisionTask[]> {
    const response = await request.get(`${API_BASE_URL}/daily-tasks`, {
      params
    })
    return response
  }

  // 获取下一个待复习任务
  static async getNextTask(params: {
    plan_id?: number
    mode?: 'normal' | 'quick'
  }): Promise<RevisionTask> {
    const response = await request.get(`${API_BASE_URL}/tasks/next`, { params })
    return response
  }

  // 批量更新任务状态
  static async batchUpdateTaskStatus(data: {
    task_ids: number[]
    status: 'completed' | 'skipped'
    mastery_level: RevisionTask['mastery_level']
    revision_mode: 'normal' | 'quick'
    time_spent?: number
    comments?: string
  }): Promise<RevisionTask[]> {
    const response = await request.post(`${API_BASE_URL}/tasks/batch`, data)
    return response
  }

  // 获取任务复习历史
  static async getTaskHistory(taskId: number): Promise<RevisionHistory[]> {
    const response = await request.get(`${API_BASE_URL}/tasks/${taskId}/history`)
    return response
  }

  // 调整任务计划
  static async adjustTaskSchedule(data: {
    task_id: number
    new_date: string
    priority?: number
    comments?: string
  }): Promise<RevisionTask> {
    const response = await request.post(`${API_BASE_URL}/tasks/adjust`, data)
    return response
  }

  // 获取每日任务统计
  static async getDailySummary(date?: string): Promise<RevisionSummary> {
    const response = await request.get(`${API_BASE_URL}/tasks/daily/summary`, {
      params: { date }
    })
    return response
  }

  // 检查手册是否有复习计划
  static async checkHandbookPlans(handbookId: number): Promise<RevisionPlan[]> {
    const response = await request.get(`${API_BASE_URL}/plans/check/${handbookId}`)
    return response
  }

  // 将笔记添加到复习计划
  static async addNoteToPlan(planId: number, data: {
    note_id: number
    start_date: string
    priority: number
  }): Promise<void> {
    await request.post(`${API_BASE_URL}/plans/${planId}/notes`, {
      ...data,
      plan_id: planId
    })
  }

  /**
   * 批量添加笔记到多个复习计划
   */
  static async addNoteToPlansBatch(data: {
    note_id: number
    plan_ids: number[]
    start_date?: string
    priority?: number
  }): Promise<AddNoteToPlansBatchResult> {
    const response = await request.post(`${API_BASE_URL}/plans/notes/batch`, data)
    return response
  }
} 