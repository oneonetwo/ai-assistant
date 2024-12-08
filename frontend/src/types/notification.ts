export interface NotificationSettings {
  id: number
  reminder_enabled: boolean
  reminder_time: string
  created_at: string
  updated_at: string
}

export interface NotificationSummary {
  pending_tasks: number
  upcoming_tasks: number
  completed_tasks: number
  suggestions: Array<{
    id: number
    title: string
    priority: number
  }>
}

export interface UpdateSettingsRequest {
  reminder_enabled: boolean
  reminder_time: string
} 