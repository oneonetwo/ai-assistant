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
    @click="handleCodeClick"
  >
    <!-- 如果是引用消息，显示引用内容 -->
    <MessageQuote
      v-if="message.quote"
      :message="message.quote"
    />
    
    <div class="message-main">
      <div class="message-avatar">
        <van-image
          :src="isUser ? '/avatar-user.png' : '/avatar-assistant.png'"
          width="40"
          height="40"
          radius="4"
        />
      </div>
      
      <div class="message-content">
        <div 
          class="message-text"
          :class="{ 'markdown-body': !isUser }"
          v-html="formattedContent"
        />
        
        <div class="message-footer">
          <span class="message-time">
            {{ new Date(message.timestamp).toLocaleString() }}
          </span>
          
          <div class="message-actions">
            <van-button
              size="mini"
              icon="ellipsis"
              @click.stop="showMessageActions"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 代码片段收藏组件 -->
  <CodeSnippets ref="codeSnippetsRef" />
  
  <!-- 消息编辑组件 -->
  <MessageEditor
    v-model:show="showEditor"
    :message="message"
    @save="handleEdit"
  />
</template>

<style scoped lang="scss">
.message {
  display: flex;
  padding: var(--van-padding-sm);
  gap: var(--van-padding-sm);
  position: relative;
  animation: message-appear 0.3s ease-out;
  
  &-user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-text {
      background-color: var(--van-primary-color);
      color: var(--van-white);
    }
  }
  
  &.message-sending {
    opacity: 0.8;
  }
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: var(--van-padding-xs);
  max-width: 80%;
  
  img {
    max-width: 100%;
    border-radius: 8px;
    cursor: zoom-in;
    transition: opacity 0.2s;
    
    &:hover {
      opacity: 0.9;
    }
  }
}

.message-text {
  padding: var(--van-padding-sm);
  background-color: var(--van-background-2);
  border-radius: var(--van-radius-lg);
  word-break: break-word;
  
  :deep(pre) {
    margin: var(--van-padding-sm) 0;
    padding: var(--van-padding-sm);
    background-color: var(--van-gray-8);
    border-radius: var(--van-radius-md);
    overflow-x: auto;
    
    code {
      background-color: transparent;
      padding: 0;
    }
  }
  
  :deep(code) {
    background-color: var(--van-gray-2);
    padding: 2px 4px;
    border-radius: var(--van-radius-sm);
  }
  
  :deep(p) {
    margin: var(--van-padding-xs) 0;
    
    &:first-child {
      margin-top: 0;
    }
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

.message-actions {
  display: flex;
  gap: var(--van-padding-xs);
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
  
  .message-content {
    max-width: 90%;
  }
}

.message-error {
  .message-text {
    border: 1px solid var(--van-danger-color);
  }
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
}

.message-status {
  position: absolute;
  right: -24px;
  top: 50%;
  transform: translateY(-50%);
}

@keyframes message-appear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-main {
  display: flex;
  gap: var(--van-padding-sm);
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--van-padding-xs);
  
  .message-time {
    font-size: 12px;
    color: var(--van-text-color-2);
  }
}

.message-actions {
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
