import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)
  
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  function updateTheme(e: MediaQueryListEvent | MediaQueryList) {
    // isDark.value = e.matches
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  }
  
  // 初始化主题
  updateTheme(mediaQuery)
  mediaQuery.addEventListener('change', updateTheme)
  
  // 手动切换主题
  function toggleTheme() {
    isDark.value = !isDark.value
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  }
  
  return {
    isDark,
    toggleTheme
  }
}) 