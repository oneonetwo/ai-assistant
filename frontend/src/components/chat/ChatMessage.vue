<template>
  <div class="message" :class="message.role">
    <div class="avatar">
      {{ message.role === 'assistant' ? 'AI' : '你' }}
    </div>
    <div class="content">
      <div class="bubble">
        <div class="markdown-body" v-html="renderedContent" />
      </div>
      <Transition name="fade">
        <div v-if="showActions" class="actions">
          <van-button size="mini" @click="$emit('quote', message)">
            <template #icon><svg-icon name="quote" /></template>
            引用
          </van-button>
          <van-button size="mini" @click="handleCopy">
            <template #icon><svg-icon name="copy" /></template>
            复制
          </van-button>
          <van-button size="mini" @click="$emit('edit', message)">
            <template #icon><svg-icon name="edit" /></template>
            编辑
          </van-button>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { computed, watch } from 'vue'



const props = defineProps<{
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
  }
}>()

const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  }
})

const renderedContent = computed(() => {
  return md.render(props.message.content)
})

//  监听message
watch(() => props.message, () => {
  console.log('message>>>>>>>>>>>', props.message)
})
</script>

<style lang="scss" scoped>
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: fade-in 0.3s var(--message-animation-timing);
  
  &.user {
    flex-direction: row-reverse;
    
    .content {
      align-items: flex-end;
      
      .bubble {
        background: var(--chat-user-bg);
        color: var(--chat-user-text);
        border-radius: var(--chat-border-radius) 0 var(--chat-border-radius) var(--chat-border-radius);
      }
      
      .actions {
        justify-content: flex-end;
      }
    }
  }
  
  .content {
    flex: 1;
    max-width: 85%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .bubble {
      padding: 12px 16px;
      background: var(--chat-ai-bg);
      color: var(--chat-ai-text);
      border-radius: 0 var(--chat-border-radius) var(--chat-border-radius) var(--chat-border-radius);
      word-break: break-word;
      
      :deep(.markdown-body) {
        font-size: 14px;
        line-height: 1.6;
        
        pre {
          margin: 12px 0;
          padding: 12px;
          border-radius: 4px;
          background: var(--code-background);
          overflow-x: auto;
          
          code {
            font-family: var(--van-font-family-code);
            font-size: 13px;
          }
        }
      }
    }
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--message-animation-duration) var(--message-animation-timing);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
