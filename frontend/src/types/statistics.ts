export interface StudyTimeStats {
  total_hours: number
  daily_average: number
  weekly_trend: WeeklyTrend[]
  peak_periods: PeakPeriod[]
}

export interface WeeklyTrend {
  date: string
  hours: number
}

export interface PeakPeriod {
  period: string
  hours: number
}

export interface MasteryStats {
  total_points: number
  mastered: number
  learning: number
  struggling: number
  mastery_rate: number
  category_distribution: Record<string, number>
}

// ... 其他统计相关的类型定义 