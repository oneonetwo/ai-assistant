<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import LoadingMessage from '@/components/chat/LoadingMessage.vue'
import MessageSkeleton from '@/components/chat/MessageSkeleton.vue'
import MessageQuote from '@/components/chat/MessageQuote.vue'
import ConversationList from '@/components/chat/ConversationList.vue'
import { useVirtualList } from '@vueuse/core'
import WelcomeScreen from '@/components/chat/WelcomeScreen.vue'

const chatStore = useChatStore()
const inputRef = ref<InstanceType<typeof ChatInput>>()
const quotedMessage = ref<Message | null>(null)
const isInitialLoading = ref(true)
const inputText = ref('')

// 虚拟列表配置
const MESSAGE_HEIGHT = 100
const containerRef = ref<HTMLElement>()
const { list: visibleMessages, containerProps, wrapperProps } = useVirtualList(
  computed(() => chatStore.currentMessages),
  {
    itemHeight: MESSAGE_HEIGHT,
    overscan: 5
  }
)

onMounted(async () => {
  try {
    await chatStore.initializeChat()
  } finally {
    isInitialLoading.value = false
  }
})

// 处理消息引用
function handleQuote(message: Message) {
  quotedMessage.value = message
  // 聚焦输入框
  inputRef.value?.focus()
}

// 处理消息发送
async function handleSend(content: string) {
  if (!content.trim()) return
  
  await chatStore.sendMessage(content, {
    quote: quotedMessage.value || undefined
  })
  
  // 清除引用和输入内容
  quotedMessage.value = null
  inputText.value = ''
}

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

// 添加滚动监听
const isAtBottom = ref(true)
const handleScroll = () => {
  if (!containerRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = containerRef.value
  isAtBottom.value = scrollHeight - scrollTop - clientHeight < 50
}

onMounted(() => {
  containerRef.value?.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  containerRef.value?.removeEventListener('scroll', handleScroll)
})

// 添加侧边栏控制
const showSidebar = ref(window.innerWidth > 768)
const isMobile = computed(() => window.innerWidth <= 768)

// 处理窗口大小变化
function handleResize() {
  if (!isMobile.value) {
    showSidebar.value = true
  }
}

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize() // 初始化时执行一次
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 移动端切换侧边栏
function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

// 监听   chatStore.currentMessages

// 处理功能标签点击
async function handleFeatureSelect(tag: { id: number, label: string, prompt: string }) {
  try {
    // 设置输入文本
    inputText.value = tag.prompt
    
    // 等待 DOM 更新后聚焦输入框
    await nextTick()
    inputRef.value?.focus()
    
    // 自动发送消息
    await handleSend(tag.prompt)
  } catch (error) {
    console.error('处理功能标签失败:', error)
  }
}
</script>

<template>
  <div class="chat-view">
    <!-- 欢迎界面 -->
    <WelcomeScreen v-if="!chatStore.currentMessages.length" @select="handleFeatureSelect" />
    
    <!-- 消息列表 -->
    <div v-else class="chat-container">
      <div 
        ref="containerRef"
        class="message-container" 
        v-bind="containerProps"
      >
        <div v-bind="wrapperProps">
          <template v-if="!isInitialLoading">
            <ChatMessage
              v-for="{ index, data } in visibleMessages"
              :key="data.id"
              :message="data"
              :show-actions="true"
              @quote="handleQuote"
            />
          </template>
          <MessageSkeleton v-else />
        </div>
      </div>

      <div class="input-wrapper">
        <MessageQuote
          v-if="quotedMessage"
          :message="quotedMessage"
          class="quoted-message"
        >
          <template #extra>
            <van-button
              size="mini"
              icon="cross"
              @click="quotedMessage = null"
            />
          </template>
        </MessageQuote>
        
        <ChatInput
          ref="inputRef"
          v-model="inputText"
          :loading="chatStore.isLoading"
          @send="handleSend"
        />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 100px; // 为底部输入区域留出空间
}

.input-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);
  padding: 12px;
  z-index: 10;
  
  .quoted-message {
    margin-bottom: 8px;
  }
}
</style> 