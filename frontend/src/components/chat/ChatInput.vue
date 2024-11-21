<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { Message } from '@/types/chat'
import { useVoiceRecognition } from '@/composables/useVoiceRecognition'
import { useSettings } from '@/composables/useSettings'

const props = defineProps<{
  isLoading?: boolean
  quotedMessage?: Message | null
}>()

const emit = defineEmits<{
  (e: 'send', text: string): void
  (e: 'update:quotedMessage', message: Message | null): void
}>()

const textareaRef = ref<HTMLTextAreaElement>()
const inputText = ref('')
const isVoiceMode = ref(false)
const showSettings = ref(false)

// 语音识别
const { 
  isRecording, 
  startRecording, 
  stopRecording 
} = useVoiceRecognition({
  onResult: (text) => {
    inputText.value = text
    handleSend()
  }
})

// 设置
const { settings } = useSettings()

// 计算属性
const textareaRows = computed(() => {
  const lines = inputText.value.split('\n').length
  return Math.min(Math.max(1, lines), 6)
})

const canSend = computed(() => 
  !props.isLoading && inputText.value.trim().length > 0
)

const placeholder = computed(() => 
  isVoiceMode.value ? '按住说话' : '输入消息...'
)

// 方法
function autoResize() {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
  }
}

async function handleSend() {
  if (!inputText.value.trim() || props.isLoading) return
  
  try {
    props.isLoading = true
    await emit('send', inputText.value)
    inputText.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    props.isLoading = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleVoiceText(text: string) {
  inputText.value = text
  isVoiceMode.value = false
}

function handleTemplateSelect(content: string) {
  inputText.value = content
  isVoiceMode.value = false
}
</script>

<template>
  <div class="chat-input">
    <!-- 引用消息预览 -->
    <div v-if="quotedMessage" class="quote-preview">
      <div class="quote-content">
        <van-icon name="quote" />
        <span>{{ quotedMessage.content }}</span>
      </div>
      <van-button
        size="mini"
        icon="cross"
        @click="$emit('update:quotedMessage', null)"
      />
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <van-button
        size="small"
        icon="voice-o"
        :class="{ active: isVoiceMode }"
        @click="toggleVoiceMode"
      />
      <van-button
        size="small"
        icon="photo-o"
        @click="handleUploadImage"
      />
      <van-button
        size="small"
        icon="setting-o"
        @click="showSettings = true"
      />
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div 
        v-if="isVoiceMode" 
        class="voice-input"
        @touchstart="startVoiceRecord"
        @touchend="stopVoiceRecord"
      >
        <van-icon :name="isRecording ? 'volume' : 'voice-o'" />
        <span>{{ isRecording ? '松开发送' : '按住说话' }}</span>
      </div>
      
      <template v-else>
        <textarea
          ref="textareaRef"
          v-model="inputText"
          class="text-input"
          :rows="textareaRows"
          :placeholder="placeholder"
          @keydown.enter.prevent="handleEnter"
          @input="autoResize"
        />
        
        <van-button
          class="send-btn"
          :disabled="!canSend"
          @click="handleSend"
        >
          <template #icon>
            <van-icon :name="isLoading ? 'loading' : 'arrow-up'" />
          </template>
        </van-button>
      </template>
    </div>

    <!-- 设置面板 -->
    <van-popup
      v-model:show="showSettings"
      position="bottom"
      class="settings-popup"
    >
      <div class="settings-header">
        <span>设置</span>
        <van-button
          icon="cross"
          @click="showSettings = false"
        />
      </div>
      <div class="settings-content">
        <van-cell-group>
          <van-cell title="连续对话">
            <template #right-icon>
              <van-switch v-model="settings.continuousDialogue" />
            </template>
          </van-cell>
          <van-cell title="代码高亮">
            <template #right-icon>
              <van-switch v-model="settings.codeHighlight" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.chat-input {
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);
  padding: 0.75rem 1rem;
}

.quote-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  margin-bottom: 0.75rem;
  background: var(--van-active-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  
  .quote-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--van-text-color-2);
    
    .van-icon {
      font-size: 1rem;
    }
  }
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  
  .van-button {
    --van-button-small-height: 32px;
    border: 1px solid var(--van-border-color);
    background: var(--van-background);
    color: var(--van-text-color-2);
    
    &:hover, &.active {
      background: var(--van-active-color);
      color: var(--van-text-color);
    }
  }
}

.input-area {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.voice-input {
  flex: 1;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: var(--van-active-color);
  border-radius: var(--radius-md);
  color: var(--van-text-color);
  cursor: pointer;
  user-select: none;
  
  &:active {
    background: var(--van-primary-color-light);
  }
  
  .van-icon {
    font-size: 1.25rem;
  }
}

.text-input {
  flex: 1;
  min-height: 44px;
  max-height: 200px;
  padding: 0.75rem;
  border: 1px solid var(--van-border-color);
  border-radius: var(--radius-md);
  background: var(--van-background);
  color: var(--van-text-color);
  font-size: 0.875rem;
  line-height: 1.5;
  resize: none;
  
  &:focus {
    outline: none;
    border-color: var(--van-primary-color);
  }
  
  &::placeholder {
    color: var(--van-text-color-2);
  }
}

.send-btn {
  width: 44px;
  height: 44px;
  padding: 0;
  border: none;
  border-radius: var(--radius-md);
  background: var(--van-primary-color);
  color: white;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .van-icon {
    font-size: 1.25rem;
  }
}

.settings-popup {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  overflow: hidden;
}

.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid var(--van-border-color);
  font-size: 1rem;
  font-weight: 500;
}

// 移动端适配
@media (max-width: 768px) {
  .chat-input {
    padding: 0.5rem;
  }
  
  .toolbar {
    margin-bottom: 0.5rem;
  }
  
  .text-input {
    font-size: 1rem; // 移动端字体稍大
  }
}
</style> 