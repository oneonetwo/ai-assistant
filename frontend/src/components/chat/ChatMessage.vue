<template>
  <div 
    class="message" 
    :class="[
      message.role,
      { 'selectable': isSelectable },
      { 'selected': isSelected }
    ]"
    @click="handleMessageClick"
  >
    <div class="select-box" v-if="isSelectable" @:click.stop="handleSelect">
      <van-checkbox 
        :model-value="isChecked"
      />
    </div>
    <div class="avatar">
      {{ message.role === 'assistant' ? 'AI' : '你' }}
    </div>
    <div class="content">
      <div v-if="message.file" class="file-preview">
        <div class="image-preview" v-if="message.file && isImage(message.file.file_type)">
          <img 
            :src="message.file.file_path" 
            :alt="message.file.original_name"
            @click="handleImageClick"
          >
          <ImagePreview
            ref="imagePreviewRef"
            :src="message.file.file_path"
          />
        </div>
        <div v-else class="file-info">
          <svg-icon :name="getFileIcon(message.file.file_type)" />
          <span>{{ message.file.original_name }}</span>
          <van-button size="mini" @click="downloadFile(message.file)">
            下载
          </van-button>
        </div>
      </div>

      <div class="bubble">
        <div class="markdown-body" v-html="renderedContent" />
      </div>
      <Transition name="fade">
        <div v-if="showActions && !isSelectable" class="actions">
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
    file?: {
      file_path: string
      original_name: string
      file_type: string
    }
  }
  showActions?: boolean
  isSelectable?: boolean
  isSelected?: boolean
}>()

const isChecked = computed(() => props.isSelected)

const emit = defineEmits<{
  (e: 'quote', message: Message): void
  (e: 'edit', message: Message): void
  (e: 'copy', message: Message): void
  (e: 'select', messageId: string): void
}>()
const handleSelect = (e: any) => {
  emit('select', props.message.id)
}

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

function isImage(fileType: string) {
  return fileType.startsWith('image')
}

function getFileIcon(fileType: string) {
  if (fileType.startsWith('image/')) return 'image'
  if (fileType.startsWith('video/')) return 'video'
  if (fileType.startsWith('audio/')) return 'audio'
  if (fileType.includes('pdf')) return 'pdf'
  if (fileType.includes('word')) return 'word'
  if (fileType.includes('excel')) return 'excel'
  return 'file'
}

function downloadFile(file: {
  file_path: string
  original_name: string
}) {
  const link = document.createElement('a')
  link.href = file.file_path
  link.download = file.original_name
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
    console.log('content changed**************', newContent)
    // 处理 content 变化的逻辑
  }
)

function handleMessageClick() {
  if (props.isSelectable) {
    emit('select', props.message.id)
  }
}
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

.message {
  position: relative;
  
  &.selectable {
    padding-right: 40px;
    
    &:hover {
      background: var(--van-background-2);
    }
    
    &.selected {
      background: var(--van-primary-light);
    }
  }
  
  .select-box {
    position: absolute;
    right: 12px;
    top: 12px;
    z-index: 1;
    opacity: 0;
    transition: opacity 0.2s;
    
    .van-checkbox {
      padding: 4px;
      border-radius: 4px;
      background: var(--van-background);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  }
  
  .select-box {
    opacity: 1;
  }
  
  &.selected .select-box {
    opacity: 1;
  }
}

.select-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 0;
  
  .van-button {
    border-radius: 16px;
    padding: 0 16px;
    
    &--primary {
      background: var(--van-primary-color);
      border: none;
      
      &:disabled {
        opacity: 0.6;
      }
    }
  }
}
</style>
