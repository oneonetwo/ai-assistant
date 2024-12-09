<script setup lang="ts">
import { ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import VoiceInput from './VoiceInput.vue'
import { showToast } from 'vant'
import UploadProgress from './UploadProgress.vue'

const props = defineProps<{
  quotedMessage?: Message | null
}>()

const emit = defineEmits<{
  (e: 'quote-remove'): void
}>()

const messageText = ref('')
const chatStore = useChatStore()
const { isLoading } = storeToRefs(chatStore)

const featureTags = [
  { id: 1, icon: 'image', label: '直接对话' },
  { id: 2, icon: 'chart', label: '分析数据' },
  { id: 3, icon: 'doc', label: '总结文本' },
  { id: 4, icon: 'bulb', label: '构思' },
  { id: 5, icon: 'edit', label: '帮我写' },
  { id: 6, icon: 'calculator', label: '给我做算' },
  { id: 7, icon: 'analyze', label: '分析图片' },
  { id: 8, icon: 'code', label: '代码' }
]

// 新增的状态
const uploadedFile = ref<File | null>(null)
const uploadProgress = ref(0)
const uploadController = ref<AbortController | null>(null)

// 文件类型映射
const FILE_TYPES = {
  IMAGE: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/bmp'
  ],
  DOCUMENT: [
    'text/plain',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'text/markdown',
    'application/json'
  ],
  AUDIO: [
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/x-m4a',
    'audio/aac'
  ]
} as const

// 判断文件类型
function getFileType(file: File) {
  if (FILE_TYPES.IMAGE.includes(file.type)) return 'image'
  if (FILE_TYPES.DOCUMENT.includes(file.type)) return 'document'
  if (FILE_TYPES.AUDIO.includes(file.type)) return 'audio'
  return null
}

// 处理文件上传
const handleFileUpload = async (file: { file: File }) => {
  const uploadFile = file.file
  const fileType = getFileType(uploadFile)
  
  if (!fileType) {
    showToast('不支持的文件类型')
    return
  }

  uploadedFile.value = uploadFile

  // 根据文件类型设置默认提示文本
  messageText.value = fileType === 'image' 
    ? '请帮我分析这张图片：\n' + (messageText.value || '')
    : fileType === 'audio'
    ? '请帮我分析这段音频：\n' + (messageText.value || '')
    : '请帮我分析这个文件：\n' + (messageText.value || '')
}

// 移除文件
const removeFile = () => {
  uploadedFile.value = null
  uploadProgress.value = 0
  if (uploadController.value) {
    uploadController.value.abort()
    uploadController.value = null
  }
}

// 获取文件图标
const getFileIcon = (fileType: string) => {
  if (fileType.startsWith('image/')) return 'image'
  if (fileType.startsWith('audio/')) return 'audio'
  if (fileType === 'application/pdf') return 'pdf'
  if (fileType === 'text/plain') return 'txt'
  if (fileType.includes('word')) return 'doc'
  if (fileType.includes('sheet') || fileType.includes('excel')) return 'excel'
  if (fileType.includes('presentation') || fileType.includes('powerpoint')) return 'ppt'
  return 'file'
}

// 处理发送消息
async function handleSend() {
  if (!messageText.value.trim() && !uploadedFile.value) return
  
  try {
    if (uploadedFile.value) {
      uploadController.value = new AbortController()
      const fileType = getFileType(uploadedFile.value)
      const isImage = fileType === 'image'
      const isAudio = fileType === 'audio'

      if (isAudio) {
        // 使用音频专用的发送方法
        await chatStore.sendAudioMessage(
          messageText.value,
          uploadedFile.value,
          {
            onProgress: (progress) => {
              uploadProgress.value = progress
            },
            onEnd: () => {
              handleOnEnd()
            },
            signal: uploadController.value.signal
          }
        )
      } else {
        // 使用通用的文件发送方法
        await chatStore.sendMessageWithFile(
          messageText.value,
          uploadedFile.value,
          {
            systemPrompt: isImage ? '请分析这张图片' : undefined,
            extractText: isImage ? true : undefined,
            onProgress: (progress) => {
              uploadProgress.value = progress
            },
            onEnd: () => {
              handleOnEnd()
            },
            signal: uploadController.value.signal
          }
        )
      }
      
      // 重置文件上传状态
      uploadedFile.value = null
      uploadProgress.value = 0
    } else {
      // 普通文本消息
      await chatStore.sendMessage(messageText.value, {
        quote: props.quotedMessage || undefined,
        onEnd: () => {
          handleOnEnd()
        }
      })
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      showToast('已取消上传')
    } else {
      showToast('发送失败')
      console.error('发送失败:', error)
    }
  }
}

// 处理发送完成
function handleOnEnd() {
  messageText.value = ''
  emit('quote-remove')
  uploadController.value = null
  uploadProgress.value = 0
  uploadedFile.value = null
}

// 文件预览
function getFilePreview(file: File) {
  if (FILE_TYPES.IMAGE.includes(file.type)) {
    return URL.createObjectURL(file)
  }
  return null
}
</script>

<template>
  <div class="chat-input">
    <div class="toolbar">
      
      <van-uploader
      accept=".txt,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.epub,.md,.json,image/*,.mp3,.wav,.ogg,.m4a,.aac"
      :max-size="30 * 1024 * 1024"
      :max-count="1"
      :before-read="beforeUpload"
      :after-read="handleFileUpload"
      >
      <van-button size="small" icon="photograph">
        上传文件
      </van-button>
    </van-uploader>
    
    <VoiceInput @input="handleVoiceInput" />
    <!-- 选择模式切换按钮 -->
    <slot name="toolbar-right" />
    </div>
    
    <div class="input-area">
      <van-field
        v-model="messageText"
        type="textarea"
        placeholder="输入消息，Shift + Enter 换行"
        rows="3"
        autosize
        @keydown.enter="(e: KeyboardEvent) => {
          if (!e.shiftKey) {
            e.preventDefault()
            handleSend()
          }
        }"
        ref="inputRef"
      >
        <template #button>
          <van-button
            type="primary"
            :loading="isLoading"
            :disabled="!messageText.trim() && !uploadedFile"
            @click="handleSend"
          >
            发送
          </van-button>
        </template>
      </van-field>

      <!-- 文件预览区域 -->
      <div v-if="uploadedFile" class="file-preview">
        <div class="file-info">
          <template v-if="getFilePreview(uploadedFile)">
            <img 
              :src="getFilePreview(uploadedFile)" 
              class="preview-image"
              alt="preview"
            />
          </template>
          <template v-else>
            <svg-icon :name="getFileIcon(uploadedFile.type)" />
          </template>
          
          <span class="file-name">{{ uploadedFile.name }}</span>
          <span class="file-size">{{ (uploadedFile.size / 1024).toFixed(1) }}KB</span>
          <van-icon name="cross" @click="removeFile" />
        </div>

        <UploadProgress 
          v-if="uploadProgress > 0 && uploadProgress < 100"
          :progress="uploadProgress"
          @cancel="cancelUpload"
        />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-input {
  padding: 16px;
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);

  .feature-tags {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    overflow-x: auto;
    padding-bottom: 8px;

    .tag {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border-radius: 16px;
      background: var(--van-background-2);
      cursor: pointer;
      white-space: nowrap;
      transition: background 0.2s;

      &:hover {
        background: var(--van-active-color);
      }

      .svg-icon {
        width: 16px;
        height: 16px;
        color: var(--van-primary-color);
      }
    }
  }

  .input-area {
    position: relative;

    .action-buttons {
      display: flex;
      gap: 8px;
      margin-left: 8px;
    }
  }
}

.quoted-message {
  padding: 8px 12px;
  background: var(--van-background-2);
  border-bottom: 1px solid var(--van-border-color);
  
  .quote-content {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .quote-text {
      flex: 1;
      font-size: 14px;
      color: var(--van-text-color);
    }
  }
}

.toolbar {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid var(--van-border-color);
}

.file-preview {
  margin-top: 8px;
  padding: 8px;
  background: var(--van-background-2);
  border-radius: 4px;

  .file-info {
    display: flex;
    align-items: center;
    gap: 8px;

    .preview-image {
      width: 40px;
      height: 40px;
      object-fit: cover;
      border-radius: 4px;
    }

    .file-name {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-size {
      color: var(--van-gray-6);
      font-size: 12px;
    }

    .svg-icon {
      width: 24px;
      height: 24px;
    }

    .van-icon {
      cursor: pointer;
      color: var(--van-gray-6);
      padding: 4px;
      
      &:hover {
        color: var(--van-danger-color);
      }
    }
  }
}

// 添加上传进度条样式
.upload-progress {
  margin-top: 8px;
  
  .progress-bar {
    height: 4px;
    background: var(--van-primary-color);
    border-radius: 2px;
    transition: width 0.3s;
  }

  .cancel-button {
    margin-top: 4px;
    text-align: right;
  }
}
</style> 