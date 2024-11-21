<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import VoiceInput from './VoiceInput.vue'
import PromptTemplates from './PromptTemplates.vue'

const chatStore = useChatStore()
const messageInput = ref('')
const isLoading = ref(false)
const showVoiceInput = ref(false)
const showTemplates = ref(false)

async function handleSend() {
  if (!messageInput.value.trim() || isLoading.value) return
  
  try {
    isLoading.value = true
    await chatStore.sendMessage(messageInput.value)
    messageInput.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleVoiceText(text: string) {
  messageInput.value = text
  showVoiceInput.value = false
}

function handleTemplateSelect(content: string) {
  messageInput.value = content
  showTemplates.value = false
}
</script>

<template>
  <div class="chat-input">
    <div class="input-container">
      <van-field
        v-model="messageInput"
        type="textarea"
        placeholder="输入消息..."
        :rows="1"
        autosize
        @keydown.enter.prevent="handleSend"
      >
        <template #button>
          <van-button
            size="small"
            icon="description"
            @click="showTemplates = true"
          />
        </template>
      </van-field>
      
      <div class="action-buttons">
        <van-button
          size="small"
          icon="microphone-o"
          @click="showVoiceInput = !showVoiceInput"
        />
        
        <van-button
          type="primary"
          size="small"
          icon="send-o"
          :loading="isLoading"
          :disabled="!messageInput.trim()"
          @click="handleSend"
        />
      </div>
    </div>
    
    <transition name="slide-up">
      <div v-if="showVoiceInput" class="voice-input-container">
        <VoiceInput @text="handleVoiceText" />
      </div>
    </transition>
    
    <van-popup
      v-model:show="showTemplates"
      position="bottom"
      :style="{ height: '60%' }"
    >
      <PromptTemplates @select="handleTemplateSelect" />
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.chat-input {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--sidebar-bg);
  border-radius: 8px;
  padding: 12px;
  
  textarea {
    flex: 1;
    border: none;
    background: transparent;
    resize: none;
    color: var(--text-color);
    font-size: 16px;
    line-height: 1.5;
    max-height: 200px;
    
    &:focus {
      outline: none;
    }
    
    &::placeholder {
      color: var(--van-gray-5);
    }
  }
}

.send-button {
  background: var(--primary-color);
  border: none;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .van-icon {
    font-size: 20px;
    color: var(--text-color);
  }
}

.hint-text {
  text-align: center;
  font-size: 12px;
  color: var(--van-gray-5);
  margin-top: 8px;
}

.voice-input-container {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  padding: var(--van-padding-sm);
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);
  
  &.slide-up-enter-active,
  &.slide-up-leave-active {
    transition: transform 0.3s ease;
  }
  
  &.slide-up-enter-from,
  &.slide-up-leave-to {
    transform: translateY(100%);
  }
}
</style> 