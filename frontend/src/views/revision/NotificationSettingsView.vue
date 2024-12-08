<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { showToast, showLoadingToast } from 'vant'
import { notificationManager } from '@/utils/notification'
import TimePickerField from '@/components/revision/TimePickerField.vue'

const store = useNotificationStore()
const reminderEnabled = ref(false)
const reminderTime = ref('09:00')

onMounted(async () => {
  try {
    await store.fetchSettings()
    if (store.settings) {
      reminderEnabled.value = store.settings.reminder_enabled
      reminderTime.value = store.settings.reminder_time || '09:00'
    }
  } catch (error) {
    showToast('获取设置失败')
  }
})

async function handleSave() {
  if (reminderEnabled.value) {
    const hasPermission = await notificationManager.requestPermission()
    if (!hasPermission) {
      showToast('请允许通知权限以启用提醒功能')
      reminderEnabled.value = false
      return
    }
  }

  const loading = showLoadingToast({
    message: '保存中...',
    forbidClick: true,
  })
  
  try {
    await store.updateSettings({
      reminder_enabled: reminderEnabled.value,
      reminder_time: reminderTime.value
    })
    
    if (reminderEnabled.value) {
      store.startNotificationCheck()
    } else {
      store.stopNotificationCheck()
    }
    
    showToast('保存成功')
  } catch (error) {
    showToast('保存失败')
  } finally {
    loading.close()
  }
}
// 处理提醒时间变化
function handleReminderTimeChange(value: string) {
  reminderTime.value = value
}
</script>

<template>
  <div class="notification-settings">
    <van-nav-bar
      title="提醒设置"
      left-arrow
      @click-left="$router.back()"
    />
    
    <div class="settings-content">
      <van-cell-group inset>
        <van-cell center title="开启提醒">
          <template #right-icon>
            <van-switch v-model="reminderEnabled" />
          </template>
        </van-cell>
        
        <TimePickerField
          v-if="reminderEnabled"
          v-model="reminderTime"
          @update:model-value="handleReminderTimeChange"
        />
      </van-cell-group>
      
      <div class="settings-tips">
        <p>开启提醒后，系统将在设定时间通知您进行复习</p>
      </div>
    </div>
    
    <div class="settings-actions">
      <van-button 
        block 
        type="primary" 
        @click="handleSave"
      >
        保存设置
      </van-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.notification-settings {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .settings-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
  }
  
  .settings-tips {
    margin-top: 12px;
    padding: 0 12px;
    font-size: 14px;
    color: var(--van-text-color-2);
  }
  
  .settings-actions {
    padding: 16px;
    background: var(--van-background-2);
  }
}
</style> 