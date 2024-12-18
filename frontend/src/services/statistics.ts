import { request } from '@/utils/request'
import type { 
  StudyTimeStats, 
  MasteryStats,
  RevisionStats,
  TagStats,
  OverallStats,
  StatsTrend,
  CategoryStats,
  StatsDetails,
  StudySession,
  LearningProgress,
  WeeklyReport,
  MonthlyReport,
  StudyHeatmap,
  StudyStreak,
  TopicMastery,
  LearningPath,
  StudyGoal,
  StudyRecommendation
} from '@/types/statistics'

const API_BASE_URL = '/api/v1/statistics'

// 接口参数类型定义
interface GetStudyTimeParams {
  days?: number
  start_date?: string
  end_date?: string
  interval?: 'hour' | 'day' | 'week' | 'month'
  include_sessions?: boolean
}

interface GetMasteryParams {
  handbook_ids?: number[]
  category_ids?: number[]
  tag_ids?: number[]
  level?: 'basic' | 'intermediate' | 'advanced'
  include_progress?: boolean
}

interface GetRevisionParams {
  plan_ids?: number[]
  start_date?: string
  end_date?: string
  status?: 'all' | 'completed' | 'pending' | 'overdue'
  include_details?: boolean
}

interface GetTagParams {
  limit?: number
  category_ids?: number[]
  sort_by?: 'frequency' | 'recent' | 'alphabetical'
  include_unused?: boolean
}

interface ExportStatsResult {
  file_url: string
  expires_at: string
}

interface StatsSyncResult {
  success: boolean
  last_sync_at: string
  details?: {
    added: number
    updated: number
    deleted: number
  }
}

export class StatisticsAPI {
  // 基础统计数据
  static async getStudyTimeStats(params: GetStudyTimeParams = {}): Promise<StudyTimeStats> {
    const response = await request.get(`${API_BASE_URL}/study-time`, { params })
    return response
  }

  static async getMasteryStats(params: GetMasteryParams = {}): Promise<MasteryStats> {
    const response = await request.get(`${API_BASE_URL}/mastery`, { params })
    return response
  }

  static async getRevisionStats(params: GetRevisionParams = {}): Promise<RevisionStats> {
    const response = await request.get(`${API_BASE_URL}/revision`, { params })
    return response
  }

  static async getTagStats(params: GetTagParams = {}): Promise<TagStats> {
    const response = await request.get(`${API_BASE_URL}/tags`, { params })
    return response
  }

  static async getOverallStats(): Promise<OverallStats> {
    const response = await request.get(`${API_BASE_URL}/overall`)
    return response
  }

  // 趋势分析
  static async getStatsTrend(params: {
    type: 'study_time' | 'mastery' | 'revision'
    interval: 'day' | 'week' | 'month'
    start_date?: string
    end_date?: string
    include_details?: boolean
  }): Promise<StatsTrend> {
    const response = await request.get(`${API_BASE_URL}/trend`, { params })
    return response
  }

  // 分类统计
  static async getCategoryStats(params: {
    type: 'mastery' | 'revision' | 'tags'
    category_ids?: number[]
    include_subcategories?: boolean
  }): Promise<CategoryStats> {
    const response = await request.get(`${API_BASE_URL}/categories`, { params })
    return response
  }

  // 详细统计
  static async getStatsDetails(type: string, id: number): Promise<StatsDetails> {
    const response = await request.get(`${API_BASE_URL}/${type}/${id}/details`)
    return response
  }

  // 学习会话
  static async getStudySessions(params: {
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }): Promise<StudySession[]> {
    const response = await request.get(`${API_BASE_URL}/sessions`, { params })
    return response
  }

  // 学习进度
  static async getLearningProgress(params: {
    handbook_id?: number
    category_id?: number
    include_history?: boolean
  }): Promise<LearningProgress> {
    const response = await request.get(`${API_BASE_URL}/progress`, { params })
    return response
  }

  // 导出统计
  static async exportStats(data: {
    types: ('study_time' | 'mastery' | 'revision' | 'tags')[]
    format: 'pdf' | 'excel' | 'csv'
    start_date?: string
    end_date?: string
    include_details?: boolean
  }): Promise<ExportStatsResult> {
    const response = await request.post(`${API_BASE_URL}/export`, data)
    return response
  }

  // 同步统计数据
  static async syncStats(params: {
    force?: boolean
    types?: ('study_time' | 'mastery' | 'revision' | 'tags')[]
  }): Promise<StatsSyncResult> {
    const response = await request.post(`${API_BASE_URL}/sync`, { params })
    return response
  }

  // 清除统计缓存
  static async clearStatsCache(types?: ('study_time' | 'mastery' | 'revision' | 'tags')[]): Promise<void> {
    await request.post(`${API_BASE_URL}/cache/clear`, { types })
  }

  // 批量获取统计数据
  static async batchGetStats(requests: {
    type: 'study_time' | 'mastery' | 'revision' | 'tags'
    params?: Record<string, any>
  }[]): Promise<Record<string, any>> {
    const response = await request.post(`${API_BASE_URL}/batch`, { requests })
    return response
  }

  // 周报和月报
  static async getWeeklyReport(params: {
    week?: string  // YYYY-WW 格式
    include_comparison?: boolean
  }): Promise<WeeklyReport> {
    const response = await request.get(`${API_BASE_URL}/reports/weekly`, { params })
    return response
  }

  static async getMonthlyReport(params: {
    month?: string  // YYYY-MM 格式
    include_comparison?: boolean
  }): Promise<MonthlyReport> {
    const response = await request.get(`${API_BASE_URL}/reports/monthly`, { params })
    return response
  }

  // 学习热力图
  static async getStudyHeatmap(params: {
    year?: number
    type?: 'study_time' | 'revision' | 'mastery'
  }): Promise<StudyHeatmap> {
    const response = await request.get(`${API_BASE_URL}/heatmap`, { params })
    return response
  }

  // 学习连续性
  static async getStudyStreak(): Promise<StudyStreak> {
    const response = await request.get(`${API_BASE_URL}/streak`)
    return response
  }

  // 主题掌握度分析
  static async getTopicMastery(params: {
    topic_ids?: number[]
    depth?: number
    include_prerequisites?: boolean
  }): Promise<TopicMastery> {
    const response = await request.get(`${API_BASE_URL}/topics/mastery`, { params })
    return response
  }

  // 学习路径分析
  static async getLearningPath(params: {
    start_date: string
    end_date: string
    include_branches?: boolean
  }): Promise<LearningPath> {
    const response = await request.get(`${API_BASE_URL}/learning-path`, { params })
    return response
  }

  // 学习目标
  static async getStudyGoals(): Promise<StudyGoal[]> {
    const response = await request.get(`${API_BASE_URL}/goals`)
    return response
  }

  static async updateStudyGoal(goalId: number, data: {
    target: number
    deadline: string
    priority?: number
  }): Promise<StudyGoal> {
    const response = await request.patch(`${API_BASE_URL}/goals/${goalId}`, data)
    return response
  }

  // 学习建议
  static async getStudyRecommendations(params: {
    type?: 'revision' | 'mastery' | 'topic'
    limit?: number
  }): Promise<StudyRecommendation[]> {
    const response = await request.get(`${API_BASE_URL}/recommendations`, { params })
    return response
  }

  // 数据分析
  static async analyzeStudyPattern(params: {
    start_date?: string
    end_date?: string
    metrics?: string[]
  }): Promise<any> {
    const response = await request.get(`${API_BASE_URL}/analysis/pattern`, { params })
    return response
  }

  static async getPredictedProgress(params: {
    goal_id?: number
    days?: number
  }): Promise<any> {
    const response = await request.get(`${API_BASE_URL}/analysis/prediction`, { params })
    return response
  }

  // 数据比较
  static async compareStats(params: {
    type: 'study_time' | 'mastery' | 'revision'
    period1: { start: string; end: string }
    period2: { start: string; end: string }
    metrics?: string[]
  }): Promise<any> {
    const response = await request.post(`${API_BASE_URL}/compare`, params)
    return response
  }

  // 数据聚合
  static async aggregateStats(params: {
    type: 'study_time' | 'mastery' | 'revision'
    group_by: 'category' | 'tag' | 'difficulty'
    start_date?: string
    end_date?: string
  }): Promise<any> {
    const response = await request.get(`${API_BASE_URL}/aggregate`, { params })
    return response
  }

  // 自定义统计
  static async getCustomStats(query: {
    metrics: string[]
    dimensions: string[]
    filters?: Record<string, any>
    sort?: Record<string, 'asc' | 'desc'>
  }): Promise<any> {
    const response = await request.post(`${API_BASE_URL}/custom`, query)
    return response
  }
}