import { request } from '@/utils/request'
import type { RevisionPlan, RevisionTask } from '@/types/revision'

const API_BASE_URL = '/api/v1/revisions'

interface GetPlanTasksParams {
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
      mastery_level:masteryLevel
    })
    return response
  }

  // 获取每日任务
  static async getDailyTasks(): Promise<RevisionTask[]> {
    const response = await request.get(`${API_BASE_URL}/daily-tasks`)
    return response
  }
} 