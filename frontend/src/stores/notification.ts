import { defineStore } from 'pinia'
import { ref, onUnmounted } from 'vue'
import { NotificationAPI } from '@/services/notificationService'
import type { NotificationSettings, NotificationSummary } from '@/types/notification'

export const useNotificationStore = defineStore('notification', () => {
  const settings = ref<NotificationSettings | null>(null)
  const summary = ref<NotificationSummary | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  let checkInterval: number | null = null

  async function fetchSettings() {
    isLoading.value = true
    error.value = null
    try {
      settings.value = await NotificationAPI.getSettings()
    } catch (err) {
      error.value = '获取设置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateSettings(data: { reminder_enabled: boolean; reminder_time: string }) {
    isLoading.value = true
    error.value = null
    try {
      settings.value = await NotificationAPI.updateSettings(data)
    } catch (err) {
      error.value = '更新设置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSummary() {
    isLoading.value = true
    error.value = null
    try {
      summary.value = await NotificationAPI.getSummary()
    } catch (err) {
      error.value = '获取摘要失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function startNotificationCheck() {
    if (checkInterval) return
    
    // 每分钟检查一次
    checkInterval = window.setInterval(async () => {
      if (!settings.value) return
      await NotificationAPI.checkAndNotify(settings.value)
    }, 60000)
  }

  function stopNotificationCheck() {
    if (checkInterval) {
      window.clearInterval(checkInterval)
      checkInterval = null
    }
  }

  // 在组件卸载时清理定时器
  onUnmounted(() => {
    stopNotificationCheck()
  })

  return {
    settings,
    summary,
    isLoading,
    error,
    fetchSettings,
    updateSettings,
    fetchSummary,
    startNotificationCheck,
    stopNotificationCheck
  }
}) 