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
  background: var(--van-background-2);
  
  .settings-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    
    :deep {
      .van-cell-group {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        
        .van-cell {
          align-items: center;
          padding: 16px;
          font-size: 15px;
          
          &::after {
            border-color: var(--van-border-color);
          }
          
          &__title {
            color: var(--van-text-color);
            font-weight: 500;
          }
          
          .van-switch {
            &__node {
              background: var(--van-background);
            }
          }
        }
        
        // TimePickerField 相关样式
        .time-picker-field {
          .van-field {
            padding: 16px;
            
            &__value {
              color: var(--van-primary-color);
              font-size: 16px;
              font-weight: 500;
            }
          }
          
          .van-popup {
            border-radius: 16px;
            overflow: hidden;
          }
          
          .van-picker {
            &-toolbar {
              border-bottom: 1px solid var(--van-border-color);
            }
            
            &__title {
              font-weight: 500;
            }
            
            &__confirm {
              color: var(--van-primary-color);
            }
            
            &-column {
              &__item {
                color: var(--van-text-color);
                
                &--selected {
                  color: var(--van-primary-color);
                  font-weight: 500;
                }
              }
            }
          }
        }
      }
    }
  }
  
  .settings-tips {
    margin-top: 16px;
    padding: 0 16px;
    font-size: 14px;
    color: var(--van-text-color-3);
    line-height: 1.6;
  }
  
  .settings-actions {
    padding: 20px;
    background: var(--van-background-2);
    border-top: 1px solid var(--van-border-color);
    
    :deep {
      .van-button {
        height: 44px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
      }
    }
  }
}

// 暗黑主题特定样式
:root[data-theme="dark"] {
  .notification-settings {
    .settings-content {
      :deep {
        .van-cell-group {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          
          .van-cell {
            background: var(--van-background);
          }
        }
        
        .time-picker-field {
          .van-popup {
            background: var(--van-background);
            
            .van-picker {
              background: var(--van-background);
              
              &-toolbar {
                background: var(--van-background);
                
                .van-picker__title {
                  color: var(--van-text-color);
                }
                
                .van-picker__cancel,
                .van-picker__confirm {
                  color: var(--van-text-color-2);
                  
                  &:active {
                    opacity: 0.8;
                  }
                }
                
                .van-picker__confirm {
                  color: var(--van-primary-color);
                }
              }
              
              &-column {
                &__item {
                  color: var(--van-text-color-2);
                  
                  &--selected {
                    color: var(--van-text-color);
                    font-weight: 500;
                  }
                }
              }
            }
          }
          
          .van-overlay {
            background-color: rgba(0, 0, 0, 0.9);
          }
        }
      }
    }
  }
}
</style> 