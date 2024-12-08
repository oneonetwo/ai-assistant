<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

onMounted(async () => {
  try {
    await notificationStore.fetchSettings()
    if (notificationStore.settings?.reminder_enabled) {
      notificationStore.startNotificationCheck()
    }
  } catch (error) {
    console.error('初始化通知系统失败:', error)
  }
})
</script>

<template>
  <router-view />
</template>

<style lang="scss" scoped>

</style>
