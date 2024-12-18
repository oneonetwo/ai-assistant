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
function isImage(fileType: string) {
  return /image|jpg|jpeg|png|gif|bmp|tiff|ico|webp/.test(fileType)
}
// 图片预览方法
function previewImage(imagePath: string, index: number) {
  // 收集所有图片URL
  const images = note.value?.attachments
    ?.filter(att => isImage(attachmentDetails.value[att.file_id]?.file_type))
    ?.map(att => attachmentDetails.value[att.file_id].file_path) || []
  
  // 使用 ImagePreview
  ImagePreview({
    images,
    startPosition: index,
    closeable: true,
    showIndex: true,
    closeIconPosition: 'top-right',
    swipeDuration: 300,
  })
}

// Add color cycling function
let colorIndex = 0
function getNextColor(): number {
  colorIndex = (colorIndex % 5) + 1
  return colorIndex
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
            :class="['custom-tag', `color-${getNextColor()}`]"
            plain
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
              <template v-if="isImage(attachmentDetails[attachment.file_id].file_type)">
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
      <div class="messages-section" v-if="note.messages?.length">
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
    max-width: 800px; // 限制内容最大宽度
    margin: 0 auto; // 居中显示
    
    // 添加页面纸张效果
    background: var(--van-background-2);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    margin-top: var(--van-padding-md);
    margin-bottom: var(--van-padding-md);
    padding: var(--van-padding-xl);

    .meta-info {
      margin-bottom: var(--van-padding-xl);
      padding-bottom: var(--van-padding-md);
      border-bottom: 1px solid var(--van-border-color);

      .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: var(--van-padding-sm);
      }

      .status-priority {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        :deep(.van-tag) {
          padding: 4px 16px;
          font-size: 13px;
          border-radius: 16px;
          
          &.status-tag,
          &.priority-tag,
          &.share-tag {
            min-width: 80px;
            text-align: center;
          }
        }
      }
    }

    .content {
      margin-bottom: var(--van-padding-xl);
      line-height: 1.8;
      font-size: 16px;
      color: var(--van-text-color);
      
      // 添加 Markdown 内容样式
      :deep(h1, h2, h3, h4, h5, h6) {
        margin-top: 2em;
        margin-bottom: 1em;
        font-weight: 600;
        line-height: 1.25;
      }

      :deep(h1) {
        font-size: 2em;
        border-bottom: 1px solid var(--van-border-color);
        padding-bottom: 0.3em;
      }

      :deep(h2) {
        font-size: 1.5em;
        border-bottom: 1px solid var(--van-border-color);
        padding-bottom: 0.3em;
      }

      :deep(p) {
        margin: 1em 0;
        line-height: 1.8;
      }

      :deep(ul, ol) {
        padding-left: 2em;
        margin: 1em 0;
      }

      :deep(li) {
        margin: 0.5em 0;
      }

      :deep(blockquote) {
        margin: 1em 0;
        padding: 0.5em 1em;
        color: var(--van-text-color-2);
        border-left: 4px solid var(--van-primary-color);
        background: var(--van-background);
        border-radius: 4px;
      }

      :deep(code) {
        background: var(--van-background);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 0.9em;
        border: 1px solid var(--van-border-color);
      }

      :deep(pre code) {
        display: block;
        overflow-x: auto;
        padding: 1em;
        border: none;
        border-radius: 8px;
      }
    }

    .attachments {
      margin: var(--van-padding-xl) 0;
      padding: var(--van-padding-lg);
      background: var(--van-background);
      border-radius: 12px;
      border: 1px solid var(--van-border-color);

      .section-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: var(--van-padding-md);
        color: var(--van-text-color);
      }

      .attachment-list {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));

        .attachment-item {
          border-radius: 8px;
          overflow: hidden;
          transition: transform 0.2s;

          &:hover {
            transform: translateY(-2px);
          }
        }

        .image-preview {
          position: relative;
          cursor: zoom-in;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

          img {
            max-width: 120px;
            max-height: 120px;
            object-fit: cover;
            transition: transform 0.3s;
          }

          .image-name {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 8px 12px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            font-size: 13px;
            transform: translateY(100%);
            transition: transform 0.3s;
          }

          &:hover {
            img {
              transform: scale(1.05);
            }

            .image-name {
              transform: translateY(0);
            }
          }
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          background: var(--van-background);
          border-radius: 8px;
          border: 1px solid var(--van-border-color);
          transition: all 0.3s;

          &:hover {
            background: var(--van-background-2);
          }

          .file-name {
            flex: 1;
            font-size: 14px;
            @include text-ellipsis;
          }

          :deep(.van-button) {
            padding: 0 16px;
            height: 32px;
            border-radius: 16px;
          }
        }
      }
    }

    .messages-section {
      margin-top: var(--van-padding-xl);
      
      :deep(.van-cell) {
        padding: var(--van-padding-md);
        border-radius: 8px;
        margin-bottom: var(--van-padding-xs);
        background: var(--van-background);
        
        &::after {
          display: none;
        }
      }

      .message-list {
        margin-top: var(--van-padding-md);
        padding: var(--van-padding-md);
        background: var(--van-background);
        border-radius: 8px;
        border: 1px solid var(--van-border-color);
      }
    }
  }

  :deep{
    .history-btn {
      height: 32px;
      padding: 0 16px;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 500;
      
      // 添加金属质感效果
      background: linear-gradient(
        180deg, 
        var(--van-background-2) 0%,
        var(--van-background) 100%
      );
      border: 1px solid rgba(var(--van-primary-color), 0.3);
      box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.15),
        0 1px 3px rgba(0, 0, 0, 0.1);
      backdrop-filter: blur(4px);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 
          inset 0 1px 0 rgba(255, 255, 255, 0.15),
          0 4px 8px rgba(0, 0, 0, 0.1);
        border-color: var(--van-primary-color);
        
        .van-button__text {
          background: linear-gradient(
            90deg,
            var(--van-primary-color) 0%,
            var(--van-text-color) 100%
          );
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
      }
      
      &:active {
        transform: translateY(0);
        box-shadow: 
          inset 0 2px 4px rgba(0, 0, 0, 0.1),
          0 1px 2px rgba(0, 0, 0, 0.05);
      }
      
      .van-button__icon {
        font-size: 18px;
        margin-right: 4px;
        color: var(--van-primary-color);
      }
      
      .van-button__text {
        transition: all 0.3s ease;
      }
    }
  }
}

// 暗色主题适配
:root[data-theme='dark'] {
  .note-detail {
    .detail-content {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    :deep{
      .history-btn {
        background: linear-gradient(
          180deg,
          rgba(255, 255, 255, 0.08) 0%,
          rgba(255, 255, 255, 0.04) 100%
        );
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow: 
          inset 0 1px 0 rgba(255, 255, 255, 0.05),
          0 1px 3px rgba(0, 0, 0, 0.2);
        
        &:hover {
          background: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.06) 100%
          );
          border-color: var(--van-primary-color);
          box-shadow: 
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 4px 8px rgba(0, 0, 0, 0.3);
        }
        
        &:active {
          background: linear-gradient(
            180deg,
            rgba(0, 0, 0, 0.05) 0%,
            rgba(0, 0, 0, 0.1) 100%
          );
          box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.2),
            0 1px 2px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }
}

.custom-tag {
  border-radius: 16px !important;
  padding: 2px 8px !important;
  margin: 4px !important;
  border: none !important;
  font-size: 12px !important;
  
  &.color-1 {
    background-color: #00B4DB !important;
    color: #ffffff !important;
  }
  
  &.color-2 {
    background-color: #9BE36D !important;
    color: #2C5E1A !important;
  }
  
  &.color-3 {
    background-color: #A78BFA !important;
    color: #ffffff !important;
  }
  
  &.color-4 {
    background-color: #FF8C82 !important;
    color: #ffffff !important;
  }
  
  &.color-5 {
    background-color: #14B8A6 !important;
    color: #ffffff !important;
  }

  &.van-tag--plain {
    background-color: transparent !important;
    
    &.color-1 {
      border: 0.5px solid #00B4DB !important;
      color: #00B4DB !important;
      :root[data-theme="dark"] & {
        color: #ffffff !important;
      }
    }
    
    &.color-2 {
      border: 0.5px solid #9BE36D !important;
      color: #2C5E1A !important;
      :root[data-theme="dark"] & {
        color: #ffffff !important;
      }
    }
    
    &.color-3 {
      border: 0.5px solid #A78BFA !important;
      color: #A78BFA !important;
      :root[data-theme="dark"] & {
        color: #ffffff !important;
      }
    }
    
    &.color-4 {
      border: 0.5px solid #FF8C82 !important;
      color: #FF8C82 !important;
      :root[data-theme="dark"] & {
        color: #ffffff !important;
      }
    }
    
    &.color-5 {
      border: 0.5px solid #14B8A6 !important;
      color: #14B8A6 !important;
      :root[data-theme="dark"] & {
        color: #ffffff !important;
      }
    }
  }
}
</style>