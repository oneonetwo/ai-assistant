<!--
 * @Author: yangjingyuan yangjingyuan@pwrd.com
 * @Date: 2024-12-09 09:59:06
 * @LastEditors: yangjingyuan yangjingyuan@pwrd.com
 * @LastEditTime: 2024-12-11 14:21:48
 * @FilePath: \frontend\src\App.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { setToastDefaultOptions } from 'vant'



setToastDefaultOptions({ duration: 2000 });
const notificationStore = useNotificationStore()

onMounted(async () => {
  try {
    await notificationStore.fetchSettings()
    console.log(notificationStore.settings?.reminder_enabled)
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
