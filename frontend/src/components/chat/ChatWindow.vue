<template>
  <div class="chat-window">
    <VirtualList
      ref="containerRef"
      :data="messages"
      :item-height="120"
      :buffer="5"
      @scroll="handleScroll"
    >
      <template #default="{ item: msg, style }">
        <div class="message-wrapper" :style="style">
          <ChatMessage
            :message="msg"
            :show-actions="!chatStore.isLoading || msg.id !== messages[messages.length - 1]?.id"
            @quote="$emit('quote', msg)"
            @copy="handleCopy"
            @edit="handleEdit"
            @retry="handleRetry"
          />
        </div>
      </template>
    </VirtualList>

    <MessageEditor
      v-if="currentEditMessage"
      v-model:show="showEditor"
      :message="currentEditMessage"
      @save="handleSave"
    />
  </div>
</template>

<style lang="scss" scoped>
.chat-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    
    .message-wrapper {
      animation: fade-in 0.3s ease;
    }
    
    .empty-tip {
      text-align: center;
      color: var(--van-text-color-2);
      padding: 40px 0;
    }
  }
  
  .input-wrapper {
    border-top: 1px solid var(--van-border-color);
    background: var(--van-background);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import { showToast } from 'vant'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import MessageEditor from './MessageEditor.vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import VirtualList from 'vue-virtual-scroll-list'

const chatStore = useChatStore()
const { messages } = storeToRefs(chatStore)
const showEditor = ref(false)
const currentEditMessage = ref<any>(null)
const isAtBottom = ref(true)
const containerRef = ref<HTMLElement | null>(null)

// 配置 markdown 渲染器
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  },
  breaks: true,
  linkify: true
})

// 优化消息渲染
const renderMessage = computed(() => (content: string) => {
  return md.render(content)
})

// 处理消息复制
async function handleCopy(msg: any) {
  try {
    await navigator.clipboard.writeText(msg.content)
    showToast('复制成功')
  } catch (error) {
    showToast('复制失败')
  }
}

// 处理消息编辑
function handleEdit(msg: any) {
  currentEditMessage.value = msg
  showEditor.value = true
}

// 处理消息发送
async function handleSend(content: string) {
  try {
    await chatStore.sendMessage(content)
  } catch (error) {
    showToast('发送失败')
  }
}

// 处理消息保存
async function handleSave(content: string) {
  try {
    await chatStore.updateMessage(currentEditMessage.value.id, content)
    showEditor.value = false
    showToast('保存成功')
  } catch (error) {
    showToast('保存失败')
  }
}

// 添加消息重试功能
async function handleRetry(messageId: string) {
  try {
    // 获取当前消息
    const message = messages.value.find(m => m.id === messageId)
    if (!message) return
    
    // 重新发送消息
    await chatStore.sendMessage(message.content, {
      retry: true,
      messageId
    })
  } catch (error) {
    showToast('重试失败')
  }
}

// 监听消息变化,自动滚动到底部
watch(() => messages.value.length, () => {
  if (isAtBottom.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// 监听加载状态变化
watch(() => chatStore.isLoading, (newVal) => {
  if (!newVal && isAtBottom.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// 滚动到底部
const scrollToBottom = () => {
  if (!containerRef.value) return
  const scrollHeight = containerRef.value.scrollHeight
  const clientHeight = containerRef.value.clientHeight
  const maxScrollTop = scrollHeight - clientHeight
  
  containerRef.value.scrollTo({
    top: maxScrollTop,
    behavior: 'smooth'
  })
}

// 监听滚动位置
const handleScroll = () => {
  if (!containerRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = containerRef.value
  isAtBottom.value = scrollHeight - scrollTop - clientHeight < 50
}

onMounted(() => {
  containerRef.value = messagesRef.value
  containerRef.value?.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  containerRef.value?.removeEventListener('scroll', handleScroll)
})
</script> 
onUnmounted(() => {
  containerRef.value?.removeEventListener('scroll', handleScroll)
})
</script> 