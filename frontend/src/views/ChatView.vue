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

const chatStore = useChatStore()
const inputRef = ref<InstanceType<typeof ChatInput>>()
const quotedMessage = ref<Message | null>(null)
const isInitialLoading = ref(true)
const inputText = ref('')

// 虚拟列表配置
const MESSAGE_HEIGHT = 100
const containerRef = ref<HTMLElement>()
const { list: visibleMessages } = useVirtualList(
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
  
  await chatStore.sendMessage({
    content,
    quote: quotedMessage.value || undefined
  })
  
  // 清除引用和输入内容
  quotedMessage.value = null
  inputText.value = ''
}

// 滚动到底部
function scrollToBottom() {
  containerRef.value?.scrollTo({
    top: containerRef.value.scrollHeight,
    behavior: 'smooth'
  })
}

// 监听新消息，自动滚动
watch(
  () => chatStore.currentMessages?.length,
  () => {
    nextTick(scrollToBottom)
  }
)

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
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 移动端切换侧边栏
function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}
</script>

<template>
  <div class="chat-layout">
    <!-- 侧边栏 -->
    <Transition name="slide">
      <div v-if="showSidebar" class="sidebar">
        <ConversationList @select="(id) => { showSidebar = isMobile ? false : true }" />
      </div>
    </Transition>

    <!-- 主聊天区域 -->
    <div class="main-content">
      <!-- 移动端顶部导航 -->
      <div v-if="isMobile" class="mobile-header">
        <van-button 
          icon="bars"
          size="small"
          @click="toggleSidebar"
        />
        <span class="title">AI 助手</span>
      </div>

      <div class="chat-view">
        <div ref="containerRef" class="message-container">
          <template v-if="isInitialLoading">
            <MessageSkeleton :count="3" />
          </template>
          
          <template v-else>
            <VirtualList
              :container="containerRef"
              :data="chatStore.currentMessages"
              :item-height="MESSAGE_HEIGHT"
              :visible-items="visibleItems"
            >
              <template #default="{ item, style }">
                <Transition name="fade-slide" appear>
                  <div :style="style">
                    <ChatMessage 
                      :message="item"
                      @quote="handleQuote"
                    />
                  </div>
                </Transition>
              </template>
            </VirtualList>
            
            <Transition name="fade">
              <LoadingMessage v-if="chatStore.isLoading" />
            </Transition>
          </template>
        </div>

        <div class="input-area">
          <!-- 显示引用消息 -->
          <Transition name="fade">
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
          </Transition>
          
          <ChatInput
            ref="inputRef"
            v-model="inputText"
            :loading="chatStore.isLoading"
            @send="handleSend"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  background: var(--van-background-2);
}

.sidebar {
  width: 300px;
  height: 100%;
  border-right: 1px solid var(--van-border-color);
  background: var(--van-background);
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.mobile-header {
  display: none;
  padding: 8px var(--van-padding-sm);
  border-bottom: 1px solid var(--van-border-color);
  background: var(--van-background);
  
  @media (max-width: 768px) {
    display: flex;
    align-items: center;
    gap: var(--van-padding-sm);
  }
  
  .title {
    font-size: var(--van-font-size-lg);
    font-weight: 500;
  }
}

.chat-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--van-padding-sm);
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--van-gray-5);
    border-radius: 2px;
  }
}

.input-area {
  border-top: 1px solid var(--van-border-color);
  background: var(--van-background);
}

.quoted-message {
  padding: var(--van-padding-sm);
  border-bottom: 1px solid var(--van-border-color);
}

// 消息动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

// 侧边栏动画
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style> 