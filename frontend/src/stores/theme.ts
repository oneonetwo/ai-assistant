import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: true
  }),
  
  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
    },

    applyTheme() {
      // 更新 document 的 data-theme 属性
      document.documentElement.setAttribute('data-theme', this.isDark ? 'dark' : 'light')
    },

    // 初始化主题
    initTheme() {
      this.applyTheme()
    }
  },
  
  persist: true
}) 