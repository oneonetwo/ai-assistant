<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const themeOptions = [
  { text: '浅色', value: 'light' },
  { text: '深色', value: 'dark' },
  { text: '跟随系统', value: 'system' }
] as const
</script>

<template>
  <div class="theme-switch">
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