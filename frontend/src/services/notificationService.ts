import { request } from '@/utils/request'
import type { NotificationSettings, NotificationSummary, UpdateSettingsRequest } from '@/types/notification'
import { notificationManager } from '@/utils/notification'

const API_BASE = '/api/v1/revision-settings'

export class NotificationAPI {
  static async getSummary(): Promise<NotificationSummary> {
    const response = await request.get(`${API_BASE}/notifications/summary`)
    return response
  }

  static async getSettings(): Promise<NotificationSettings> {
    const response = await request.get(`${API_BASE}/settings`)
    return response
  }

  static async updateSettings(data: UpdateSettingsRequest): Promise<NotificationSettings> {
    const response = await request.patch(`${API_BASE}/settings`, data)
    return response
  }
}

export class NotificationService {
  private static checkTime(reminderTime: string): boolean {
    const [hours, minutes] = reminderTime.split(':').map(Number)
    const now = new Date()
    return now.getHours() === hours && now.getMinutes() === minutes
  }

  static async checkAndNotify(settings: NotificationSettings): Promise<void> {
    if (!settings.reminder_enabled) return

    const isTimeToNotify = this.checkTime(settings.reminder_time)
    if (!isTimeToNotify) return

    try {
      const summary = await NotificationAPI.getSummary()
      
      if (summary.pending_tasks > 0) {
        await notificationManager.show({
          title: '复习提醒',
          body: `您有 ${summary.pending_tasks} 个待复习任务`,
          onClick: () => {
            window.open('/revision/daily-summary', '_blank')
          }
        })
      }
    } catch (error) {
      console.error('检查通知失败:', error)
    }
  }
} 