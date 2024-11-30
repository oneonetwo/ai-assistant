<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import LoadingMessage from '@/components/chat/LoadingMessage.vue'
import MessageSkeleton from '@/components/chat/MessageSkeleton.vue'
import MessageQuote from '@/components/chat/MessageQuote.vue'
import ConversationList from '@/components/chat/ConversationList.vue'
import WelcomeScreen from '@/components/chat/WelcomeScreen.vue'
import { useRoute, useRouter } from 'vue-router'

const chatStore = useChatStore()
const containerRef = ref<HTMLElement | null>(null)
const inputRef = ref<InstanceType<typeof ChatInput>>()
const quotedMessage = ref<Message | null>(null)
const isInitialLoading = ref(true)
const inputText = ref('')
const selectedMessages = ref<Set<string>>(new Set())
const isSelecting = ref(false)
const route = useRoute()
const router = useRouter()

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

// 监听消息变化
watch(() => chatStore.currentMessages, (messages) => {
  if (isAtBottom.value || messages.length === 1) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { deep: true })

// 监听加载状态变化
watch(() => chatStore.isLoading, (newVal, oldVal) => {
  if (oldVal && !newVal && isAtBottom.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
})

// 计算属性: 消息选中状态
const messageSelectedState = computed(() => {
  return (messageId: string) => selectedMessages.value.has(messageId)
})

// 修改选择切换函数
function toggleMessageSelection(messageId: string) {
  console.log('toggleMessageSelection.......', messageId)
  const newSelectedMessages = new Set(selectedMessages.value)
  if (newSelectedMessages.has(messageId)) {
    newSelectedMessages.delete(messageId)
  } else {
    newSelectedMessages.add(messageId)
  }
  selectedMessages.value = newSelectedMessages
}

function handleAnalyze() {
  if (selectedMessages.value.size === 0) return
  
  const messages = chatStore.currentMessages.filter(
    msg => selectedMessages.value.has(msg.id)
  )
  
  router.push({
    name: 'analyze',
    params: {
      messages: JSON.stringify(messages),
      systemPrompt: '请对这些对话内容进行分析整理,生成一篇结构化的笔记'
    }
  })
}

// 切换选择模式
function toggleSelecting() {
  isSelecting.value = !isSelecting.value
  if (!isSelecting.value) {
    selectedMessages.value.clear()
  }
}
</script>

<template>
  <div class="chat-view">
    <!-- 保留现有的欢迎界面 -->
    <WelcomeScreen v-if="!chatStore.currentMessages.length" @select="handleFeatureSelect" />
    
    <!-- 修改消息列表部分 -->
    <div v-else class="chat-container">
      <div 
        ref="containerRef"
        class="message-container"
      >
        <template v-if="!isInitialLoading">
          <ChatMessage
            v-for="message in chatStore.currentMessages"
            :key="message.id"
            :message="message"
            :show-actions="true"
            :is-selectable="isSelecting"
            :is-selected="messageSelectedState(message.id)"
            @quote="handleQuote"
            @select="toggleMessageSelection"
          />
        </template>
        <MessageSkeleton v-else />
      </div>

      <!-- 保留现有的输入区域 -->
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
          :disabled="isSelecting"
          @send="handleSend"
        >
          <template #toolbar-right>
              <!-- 添加工具栏 -->
        <div class="toolbar-right">
          <van-button
              v-if="chatStore.currentMessages.length && !isInitialLoading && !isSelecting"
                  class="select-toggle"
                  type="primary"
                  size="small"
                  @click="toggleSelecting"
                >
                  收录到笔记
                </van-button>
                <div v-else>
                  <van-button 
                  type="primary"
                  size="small" 
                  @click="toggleSelecting"
                  >
                  取消选择
                  </van-button>

                  <van-button
                  type="primary"
                  size="small"
                  :disabled="selectedMessages.size === 0"
                  @click="handleAnalyze"
                  >
                  收录完成进行分析整理 ({{ selectedMessages.size }})
                  </van-button>
              </div>
            </div>
          </template>
        </ChatInput>
      </div>
    </div>

    <!-- 添加选择模式切换按钮 -->
  </div>
</template>

<style lang="scss" scoped>
.chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .toolbar {
    padding: 8px 16px;
    border-bottom: 1px solid var(--van-border-color);
    display: flex;
    gap: 8px;
    background: var(--van-background-2);
    position: sticky;
    top: 0;
    z-index: 10;
  }
  
  .select-toggle {
    margin-top: 2px;
  }
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
  padding-bottom: 300px; // 为底部输入区域留出空间
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