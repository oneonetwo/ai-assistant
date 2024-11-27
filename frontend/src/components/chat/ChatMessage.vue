<template>
  <div class="message" :class="message.role">
    <div class="avatar">
      {{ message.role === 'assistant' ? 'AI' : '你' }}
    </div>
    <div class="content">
      <div v-if="message.file" class="file-preview">
        <div class="image-preview" v-if="isImage(message.file.type)">
          <img 
            :src="message.file.url" 
            :alt="message.file.name"
            @click="handleImageClick"
          >
          <ImagePreview
            ref="imagePreviewRef"
            :src="message.file.url"
          />
        </div>
        <div v-else class="file-info">
          <svg-icon :name="getFileIcon(message.file.type)" />
          <span>{{ message.file.name }}</span>
          <van-button size="mini" @click="downloadFile(message.file)">
            下载
          </van-button>
        </div>
      </div>

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
import ImagePreview from './ImagePreview.vue'
import { ref } from 'vue'

const props = defineProps<{
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    file: {
      url: string
      name: string
      type: string
    }
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



const isImage = (fileType: string) => fileType.startsWith('image/')

const getFileIcon = (fileType: string) => {
  if (fileType.startsWith('image/')) return 'image'
  if (fileType === 'application/pdf') return 'pdf'
  if (fileType === 'text/plain') return 'txt'
  if (fileType.includes('word')) return 'doc'
  return 'file'
}

const downloadFile = (file: { url: string, name: string }) => {
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const imagePreviewRef = ref()

const handleImageClick = () => {
  imagePreviewRef.value?.open()
}

watch(
  () => props.message,
  (newContent) => {
    console.log('content changed', newContent)
    // 处理 content 变化的逻辑
  }
)
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

.file-preview {
  margin: 8px 0;
  max-width: 300px;
  max-height: 300px;
  .image-preview{
    max-width: 100px;
    height: 100px;
    img {
      max-width: 100%;
      max-height: 100%;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s;

      &:hover {
        transform: scale(1.02);
      }
    }
  }

  .file-info {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--van-background-2);
    border-radius: 8px;
    border: 1px solid var(--van-border-color);

    .svg-icon {
      width: 24px;
      height: 24px;
      color: var(--van-primary-color);
    }

    span {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
