<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'

const messageText = ref('')
const chatStore = useChatStore()
const { isLoading } = storeToRefs(chatStore)

// 处理回车按键
function handleEnterPress(e: KeyboardEvent) {
  // 如果是shift+enter，允许换行
  if (e.shiftKey) return

  // 如果正在加载或消息为空，不发送
  if (isLoading.value || !messageText.value.trim()) return

  handleSend()
}

// 发送消息
async function handleSend() {
  if (!messageText.value.trim()) return
  
  try {
    await chatStore.sendMessage(messageText.value)
    messageText.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}
</script>

<template>
  <div class="chat-input">
    <van-field
      v-model="messageText"
      type="textarea"
      placeholder="输入消息..."
      rows="3"
      autosize
      @keydown.enter.prevent="handleEnterPress"
      class="message-textarea"
    >
      <template #button>
        <van-button 
          :loading="isLoading"
          :disabled="!messageText.trim()"
          type="primary" 
          @click="handleSend"
        >
          发送
        </van-button>
      </template>
    </van-field>
  </div>
</template>

<style lang="scss" scoped>
.chat-input {
  padding: 12px;
  border-top: 1px solid var(--van-gray-3);
}
</style> 