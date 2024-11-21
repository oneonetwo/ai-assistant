import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: false
  }),
  
  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      // 可以在这里添加实际的主题切换逻辑
      document.documentElement.classList.toggle('dark', this.isDark)
    }
  }
}) 