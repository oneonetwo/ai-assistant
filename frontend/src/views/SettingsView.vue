<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { useLocalStorage } from '@vueuse/core'

const router = useRouter()

// 设置选项
const settings = useLocalStorage('chat-settings', {
  theme: 'light',
  language: 'zh-CN',
  fontSize: 14,
  enableVoiceInput: true,
  enableMarkdown: true,
  enableCodeHighlight: true
})

// 主题选项
const themeOptions = [
  { text: '浅色', value: 'light' },
  { text: '深色', value: 'dark' },
  { text: '跟随系统', value: 'auto' }
]

// 语言选项
const languageOptions = [
  { text: '简体中文', value: 'zh-CN' },
  { text: 'English', value: 'en-US' }
]

// 清除数据
async function handleClearData() {
  try {
    await showDialog({
      title: '确认清除',
      message: '这将清除所有聊天记录和设置，确定继续吗？',
      showCancelButton: true
    })
    
    localStorage.clear()
    showToast('数据已清除')
    router.push('/')
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <div class="settings-view">
    <van-nav-bar
      title="设置"
      left-arrow
      @click-left="router.back()"
    />
    
    <div class="settings-container">
      <van-cell-group title="外观">
        <van-cell title="主题">
          <template #right-icon>
            <van-radio-group v-model="settings.theme">
              <van-radio
                v-for="option in themeOptions"
                :key="option.value"
                :name="option.value"
              >
                {{ option.text }}
              </van-radio>
            </van-radio-group>
          </template>
        </van-cell>
        
        <van-cell title="字体大小">
          <template #right-icon>
            <van-stepper
              v-model="settings.fontSize"
              :min="12"
              :max="20"
              :step="1"
            />
          </template>
        </van-cell>
      </van-cell-group>
      
      <van-cell-group title="功能">
        <van-cell title="语音输入">
          <template #right-icon>
            <van-switch v-model="settings.enableVoiceInput" />
          </template>
        </van-cell>
        
        <van-cell title="Markdown 支持">
          <template #right-icon>
            <van-switch v-model="settings.enableMarkdown" />
          </template>
        </van-cell>
        
        <van-cell title="代码高亮">
          <template #right-icon>
            <van-switch v-model="settings.enableCodeHighlight" />
          </template>
        </van-cell>
      </van-cell-group>
      
      <van-cell-group title="数据">
        <van-cell 
          title="清除所有数据" 
          is-link
          @click="handleClearData"
        />
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.settings-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-container {
  flex: 1;
  overflow-y: auto;
  padding-bottom: var(--van-padding-md);
}
</style> 