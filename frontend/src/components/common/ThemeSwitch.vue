<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// 设置默认深色主题
themeStore.setTheme('dark')

const themeOptions = [
  { text: '浅色', value: 'light' },
  { text: '深色', value: 'dark' },
  { text: '跟随系统', value: 'system' }
] as const
</script>

<template>
  <div class="theme-switch">
    <!-- 添加主题切换按钮 -->
    <van-button
      class="theme-btn"
      :icon="themeStore.theme === 'dark' ? 'moon-o' : 'sunny-o'"
      @click="themeStore.toggleTheme()"
    />
    
    <!-- 保留下拉菜单作为备选方案 -->
    <van-dropdown-menu>
      <van-dropdown-item
        v-model="themeStore.theme"
        :options="themeOptions"
      />
    </van-dropdown-menu>
  </div>
</template>

<style lang="scss" scoped>
.theme-switch {
  margin-left: auto;
}
</style> 