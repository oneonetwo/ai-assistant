<script setup lang="ts">
import { computed, ref } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { useChatStore } from '@/stores/chat'
import { ImagePreview, showToast, showDialog } from 'vant'
import MessageQuote from './MessageQuote.vue'
import CodeSnippets from './CodeSnippets.vue'
import MessageEditor from './MessageEditor.vue'

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

interface Props {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: number
    status?: 'success' | 'error' | 'sending'
    quote?: {
      id: string
      role: 'user' | 'assistant'
      content: string
      timestamp: number
    }
  }
}

const props = defineProps<Props>()
const chatStore = useChatStore()

// 计算消息是否来自用户
const isUser = computed(() => props.message.role === 'user')

// 将 Markdown 转换为 HTML
const formattedContent = computed(() => {
  try {
    return marked(props.message.content)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    return props.message.content
  }
})

// 复制消息内容
async function copyContent(content: string) {
  try {
    await navigator.clipboard.writeText(content)
    // 使用 Vant 的 showToast
    showToast({
      message: '复制成功',
      position: 'top',
    })
  } catch (error) {
    console.error('复制失败:', error)
    showToast({
      message: '复制失败',
      type: 'fail',
      position: 'top',
    })
  }
}

function handleRetry() {
  if (props.message.role === 'user') {
    chatStore.retryMessage(props.message.id)
  }
}

// 处理图片点击
function handleImageClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target.tagName === 'IMG') {
    ImagePreview({
      images: [target.getAttribute('src')!],
      closeable: true
    })
  }
}

const messageClass = computed(() => ({
  'message-user': isUser.value,
  'message-error': props.message.status === 'error',
  'message-sending': props.message.status === 'sending'
}))

const codeSnippetsRef = ref<InstanceType<typeof CodeSnippets>>()
const showActions = ref(false)

const emit = defineEmits<{
  (e: 'quote', message: Message): void
}>()

// 处理代码块点击
function handleCodeClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  const codeBlock = target.closest('pre code')
  if (codeBlock) {
    showActions.value = true
    // 获取代码语言
    const language = Array.from(codeBlock.classList)
      .find(cls => cls !== 'hljs')
      ?.replace('language-', '') || ''
      
    // 使用 showDialog 替代 showActionSheet
    showDialog({
      title: '代码操作',
      message: '请选择操作',
      showCancelButton: true,
      confirmButtonText: '复制代码',
      cancelButtonText: '收藏代码',
      closeOnClickOverlay: true
    }).then((action) => {
      if (action === 'confirm') {
        copyContent(codeBlock.textContent || '')
      } else {
        codeSnippetsRef.value?.addSnippet(codeBlock.textContent || '', language)
      }
    }).catch(() => {
      // 用户取消操作
    })
  }
}

// 显示消息操作菜单
function showMessageActions() {
  showDialog({
    title: '消息操作',
    message: '请选择操作',
    showCancelButton: true,
    confirmButtonText: '引用回复',
    cancelButtonText: '复制内容',
    closeOnClickOverlay: true
  }).then((action) => {
    if (action === 'confirm') {
      emit('quote', props.message)
    } else {
      copyContent(props.message.content)
    }
  }).catch(() => {
    // 用户取消操作
  })
}
</script>

<template>
  <div 
    class="message" 
    :class="messageClass"
    @click="handleImageClick"
  >
    <!-- 头像 -->
    <div class="message-avatar">
      <van-image
        :src="isUser ? '/avatar-user.png' : '/avatar-ai.png'"
        width="30"
        height="30"
        radius="4"
      />
    </div>

    <div class="message-wrapper">
      <!-- 引用消息 -->
      <MessageQuote 
        v-if="message.quote"
        :message="message.quote"
        class="message-quote"
      />

      <!-- 消息内容 -->
      <div class="message-bubble">
        <div 
          class="message-content markdown-body"
          v-html="formattedContent"
        />
        
        <!-- 消息状态 -->
        <div v-if="message.status" class="message-status">
          <van-icon 
            v-if="message.status === 'sending'" 
            name="loading" 
            class="loading"
          />
          <van-icon 
            v-else-if="message.status === 'error'" 
            name="warning-o" 
            class="error"
          />
        </div>

        <!-- 消息操作 -->
        <div class="message-actions">
          <van-button
            v-if="message.status === 'error'"
            size="mini"
            icon="replay"
            @click="handleRetry"
          />
          <van-button
            size="mini"
            icon="copy-o"
            @click="copyContent(message.content)"
          />
          <van-button
            size="mini"
            icon="edit"
            @click="showEditor = true"
          />
          <van-button
            size="mini"
            icon="star-o"
            @click="handleCollect"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.message {
  display: flex;
  padding: 1.5rem;
  gap: 1rem;
  position: relative;
  transition: var(--transition-normal);
  
  &:hover {
    background: var(--van-background-2);
    
    .message-actions {
      opacity: 1;
    }
  }
  
  &-user {
    background: var(--van-background);
  }
  
  &-assistant {
    background: var(--van-background-2);
  }
}

.message-avatar {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.message-wrapper {
  flex: 1;
  min-width: 0;
  max-width: var(--max-width);
  margin: 0 auto;
}

.message-quote {
  margin-bottom: 1rem;
}

.message-bubble {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 100%;
  padding: 1rem;
  background-color: var(--van-background-2);
  border-radius: var(--van-radius-lg);
  word-break: break-word;
}

.message-content {
  flex: 1;
  min-width: 0;
  max-width: 100%;
  margin: 0 auto;
}

.message-status {
  position: absolute;
  right: -24px;
  top: 50%;
  transform: translateY(-50%);
}

.message-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
  
  .message:hover & {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .message-actions {
    opacity: 1;
  }
}
</style>
