import { defineStore } from 'pinia'
import type { SettingsState, UserSettings, ThemeMode } from '@/types/settings'

const DEFAULT_SETTINGS: UserSettings = {
  theme: 'dark',
  fontSize: 14,
  enterToSend: true,
  autoScroll: true,
  showTimestamp: true
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => ({
    settings: { ...DEFAULT_SETTINGS }
  }),

  actions: {
    updateSettings(settings: Partial<UserSettings>) {
      this.settings = {
        ...this.settings,
        ...settings
      }
      this.saveSettings()
    },

    setTheme(theme: ThemeMode) {
      this.settings.theme = theme
      this.applyTheme()
      this.saveSettings()
    },

    loadSettings() {
      const saved = localStorage.getItem('user-settings')
      if (saved) {
        this.settings = JSON.parse(saved)
        this.applyTheme()
      }
    },

    saveSettings() {
      localStorage.setItem('user-settings', JSON.stringify(this.settings))
    },

    applyTheme() {
      const theme = this.settings.theme === 'system'
        ? window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        : this.settings.theme
      
      document.documentElement.setAttribute('data-theme', theme)
    }
  }
}) 