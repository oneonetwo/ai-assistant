<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { Note, FileInfo } from '@/types/handbook'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import { showImagePreview as ImagePreview } from 'vant'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()

const noteId = route.params.id as string
const note = ref<Note | null>(null)
const showMessages = ref(false)
const attachmentDetails = ref<Record<string, FileInfo>>({})

// 添加音频播放相关的状态
const audioPlayer = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentAudioId = ref<string | null>(null)

// 图片预览相关状态
const showImagePreview = ref(false)
const previewImages = ref<string[]>([])
const currentImageIndex = ref(0)

const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

onMounted(async () => {
  await loadNote()
  await loadAttachmentDetails()
  
  // 添加音频播放结束事件监听
  const audio = new Audio()
  audio.addEventListener('ended', () => {
    isPlaying.value = false
    currentAudioId.value = null
  })
  audioPlayer.value = audio
})

onUnmounted(() => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value = null
  }
})

async function loadNote() {
  try {
    note.value = await store.fetchNote(Number(noteId))
  } catch (error) {
    showToast('加载笔记失败')
    router.back()
  }
}

async function loadAttachmentDetails() {
  if (!note.value?.attachments?.length) return
  
  const fileIds = note.value.attachments
    .map(att => att.file_id)
    .filter(Boolean) as string[]
    
  if (fileIds.length === 0) return

  try {
    const files = await store.fetchFileDetails(fileIds)
    attachmentDetails.value = files.reduce((acc, file) => {
      acc[file.file_id] = file
      return acc
    }, {} as Record<string, FileInfo>)
  } catch (error) {
    showToast('加载附件信息失败')
  }
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

const renderedContent = computed(() => {
  return note.value ? md.render(note.value.content) : ''
})

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    draft: 'default',
    published: 'success',
    archived: 'warning'
  }
  return typeMap[status] || 'default'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return textMap[status] || status
}

const getPriorityType = (priority: string) => {
  const typeMap: Record<string, string> = {
    low: 'primary',
    medium: 'warning',
    high: 'danger'
  }
  return typeMap[priority] || 'default'
}

const getPriorityText = (priority: string) => {
  const textMap: Record<string, string> = {
    low: '低优先级',
    medium: '中优先级',
    high: '高优先级'
  }
  return textMap[priority] || priority
}

function getFileIcon(mimeType: string) {
  const typeMap: Record<string, string> = {
    'application/pdf': 'file-pdf',
    'image/': 'file-image',
    'video/': 'file-video',
    'audio/': 'file-audio',
    // Add more mime type mappings as needed
  }
  
  const matchedType = Object.keys(typeMap).find(type => mimeType.startsWith(type))
  return matchedType ? typeMap[matchedType] : 'file'
}

// 跳转到复习历史
function navigateToHistory() {
  router.push(`/handbooks/notes/${noteId}/history`)
}

// 添加音频控制方法
function toggleAudioPlay(fileInfo: FileInfo) {
  if (currentAudioId.value === fileInfo.file_id) {
    if (isPlaying.value) {
      audioPlayer.value?.pause()
      isPlaying.value = false
    } else {
      audioPlayer.value?.play()
      isPlaying.value = true
    }
  } else {
    if (audioPlayer.value) {
      audioPlayer.value.pause()
      audioPlayer.value.src = fileInfo.file_path
    } else {
      audioPlayer.value = new Audio(fileInfo.file_path)
    }
    currentAudioId.value = fileInfo.file_id
    audioPlayer.value.play()
    isPlaying.value = true
  }
}

// 图片预览方法
function previewImage(imagePath: string, index: number) {
  // 收集所有图片URL
  previewImages.value = note.value?.attachments
    ?.filter(att => attachmentDetails.value[att.file_id]?.file_type?.startsWith('image/'))
    ?.map(att => attachmentDetails.value[att.file_id].file_path) || []
  
  currentImageIndex.value = index
  
  // 使用 showImagePreview
  ImagePreview({
    images: previewImages.value,
    startPosition: currentImageIndex.value,
    closeable: true,
  })
}
</script>

<template>
  <div class="note-detail" v-if="note">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      left-arrow
      :title="note.title"
      @click-left="router.back()"
      @click-right="navigateToHistory"
    >
      <template #right>
        <van-button
          class="history-btn"
          plain
          size="small"
          icon="chart-trending-o"
          @click="navigateToHistory"
        >
          复习历史
        </van-button>
      </template>
    </van-nav-bar>

    <div class="detail-content">
      <!-- <h1 class="title">{{ note.title }}</h1> -->

      <!-- 标签、状态、优先级 -->
      <div class="meta-info">
        <div class="tags">
          <van-tag 
            v-for="tag in note.tags" 
            :key="tag.id"
            type="primary"
            class="tag"
          >
            {{ tag.name }}
          </van-tag>
        </div>

        <div class="status-priority">
          <van-tag
            :type="getStatusType(note.status)"
            round
            class="status-tag"
          >
            {{ getStatusText(note.status) }}
          </van-tag>
          <van-tag
            :type="getPriorityType(note.priority)"
            round
            class="priority-tag"
          >
            {{ getPriorityText(note.priority) }}
          </van-tag>
          <van-tag
            :type="note.is_shared ? 'success' : 'warning'"
            round
            class="share-tag"
          >
            {{ note.is_shared ? '已共享' : '未共享' }}
          </van-tag>
        </div>
      </div>

      <!-- Markdown 内容 -->
      <div class="content markdown-body" v-html="renderedContent" />

      <!-- 文件列表 -->
      <div class="attachments" v-if="note.attachments?.length">
        <div class="section-title">附件</div>
        <div class="attachment-list">
          <div 
            v-for="(attachment, index) in note.attachments" 
            :key="attachment.file_id"
            class="attachment-item"
          >
            <template v-if="attachmentDetails[attachment.file_id]">
              <template v-if="attachmentDetails[attachment.file_id].file_type.startsWith('image/')">
                <div 
                  class="image-preview" 
                  @click="previewImage(attachmentDetails[attachment.file_id].file_path, index)"
                >
                  <img 
                    :src="attachmentDetails[attachment.file_id].file_path" 
                    :alt="attachmentDetails[attachment.file_id].original_name"
                  >
                  <div class="image-name">{{ attachmentDetails[attachment.file_id].original_name }}</div>
                </div>
              </template>
              <template v-else-if="attachmentDetails[attachment.file_id].mime_type === 'audio/mpeg'">
                <div class="audio-player">
                  <div class="file-info">
                    <svg-icon name="file-audio" />
                    <span class="file-name">{{ attachmentDetails[attachment.file_id].original_name }}</span>
                    <van-button 
                      size="small"
                      :icon="currentAudioId === attachment.file_id && isPlaying ? 'pause-circle-o' : 'play-circle-o'"
                      @click="toggleAudioPlay(attachmentDetails[attachment.file_id])"
                    >
                      {{ currentAudioId === attachment.file_id && isPlaying ? '暂停' : '播放' }}
                    </van-button>
                    <van-button 
                      size="small"
                      icon="download"
                      @click="downloadFile(attachmentDetails[attachment.file_id])"
                    >
                      下载
                    </van-button>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="file-info">
                  <svg-icon :name="getFileIcon(attachmentDetails[attachment.file_id].mime_type)" />
                  <span class="file-name">{{ attachmentDetails[attachment.file_id].original_name }}</span>
                  <van-button 
                    size="small"
                    icon="download"
                    @click="downloadFile(attachmentDetails[attachment.file_id])"
                  >
                    下载
                  </van-button>
                </div>
              </template>
            </template>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-section">
        <van-cell
          title="相关对话"
          is-link
          :arrow="showMessages ? 'up' : 'down'"
          @click="showMessages = !showMessages"
        />
        <div v-show="showMessages" class="message-list">
          <ChatMessage
            v-for="message in note.messages"
            :key="message.id"
            :message="message"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.note-detail {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--van-background);

  .detail-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--van-padding-md);

    .title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: var(--van-padding-md);
    }

    .meta-info {
      margin-bottom: var(--van-padding-lg);

      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: var(--van-padding-xs);
      }

      .status-priority {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        :deep(.van-tag) {
          padding: 2px 12px;
          font-size: 12px;
          
          &.status-tag {
            min-width: 60px;
            text-align: center;
          }
          
          &.priority-tag {
            min-width: 70px;
            text-align: center;
          }
          
          &.share-tag {
            min-width: 60px;
            text-align: center;
          }
        }
      }
    }

    .content {
      margin-bottom: var(--van-padding-lg);
      line-height: 1.6;
    }

    .attachments {
      margin-bottom: var(--van-padding-lg);

      .section-title {
        font-weight: 500;
        margin-bottom: var(--van-padding-xs);
      }

      .attachment-list {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));

        .attachment-item {
          border-radius: 8px;
          overflow: hidden;
        }

        .image-preview {
          position: relative;
          cursor: zoom-in;
          overflow: hidden;
          border-radius: 8px;
          border: 1px solid var(--van-border-color);
          transition: transform 0.2s;

          &:hover {
            transform: scale(1.02);

            .image-name {
              transform: translateY(0);
            }

            &::after {
              content: '';
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background: rgba(0, 0, 0, 0.1);
              pointer-events: none;
            }
          }

          img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            vertical-align: middle;
          }

          .image-name {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 8px;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            font-size: 12px;
            transform: translateY(100%);
            transition: transform 0.2s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }

        .audio-player {
          background: var(--van-background-2);
          border-radius: 8px;
          border: 1px solid var(--van-border-color);
          padding: 12px;

          .file-info {
            display: flex;
            gap: 12px;

            .file-icon {
              flex-shrink: 0;
              width: 24px;
              height: 24px;
              display: flex;
              align-items: center;
              justify-content: center;
              
              :deep(svg) {
                width: 24px;
                height: 24px;
              }
            }

            .file-details {
              flex: 1;
              min-width: 0; // 防止子元素溢出

              .file-name {
                font-size: 14px;
                margin-bottom: 8px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              }

              .file-controls {
                display: flex;
                gap: 8px;

                :deep(.van-button) {
                  flex-shrink: 0;
                  height: 28px;
                  padding: 0 12px;
                  border-radius: 14px;
                  
                  &:active {
                    opacity: 0.8;
                  }
                }
              }
            }
          }
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: var(--van-background-2);
          border-radius: 8px;
          border: 1px solid var(--van-border-color);

          .file-name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
      }
    }

    .messages-section {
      .message-list {
        margin-top: var(--van-padding-xs);
        padding: var(--van-padding-sm);
        background: var(--van-background-2);
        border-radius: 8px;
      }
    }
  }

  :deep(.history-btn) {
    // 适配暗色主题
    --van-button-plain-background: transparent;
    --van-button-default-border-color: var(--van-gray-5);
    --van-button-default-color: var(--van-text-color);
    
    // 按钮样式优化
    padding: 0 12px;
    border-radius: 16px;
    font-size: 13px;
    
    // 悬停效果
    &:active {
      opacity: 0.8;
      background: var(--van-gray-2);
    }
    
    // 图标���式
    .van-button__icon {
      margin-right: 4px;
      font-size: 16px;
    }
  }

  // 自定义 vant 图片预览样式
  :deep(.van-image-preview) {
    .van-image-preview__index {
      padding: 8px 16px;
      border-radius: 16px;
      background: rgba(0, 0, 0, 0.7);
      font-size: 14px;
    }

    .van-image-preview__close-icon {
      top: 16px;
      right: 16px;
      color: #fff;
      font-size: 22px;
    }
  }
}
</style>