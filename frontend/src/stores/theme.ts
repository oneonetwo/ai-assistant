import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

type Theme = 'light' | 'dark' | 'system'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('system')
  const systemDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)

  // 监听系统主题变化
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    systemDark.value = e.matches
  })

  // 计算当前实际使用的主题
  const currentTheme = computed(() => {
    if (theme.value === 'system') {
      return systemDark.value ? 'dark' : 'light'
    }
    return theme.value
  })

  // 监听主题变化并应用
  watch(currentTheme, (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
  }, { immediate: true })

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
  }

  return {
    theme,
    currentTheme,
    setTheme
  }
}, {
  persist: true
}) 