<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { Note } from '@/types/handbook'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import ChatMessage from '@/components/chat/ChatMessage.vue'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()

const noteId = route.params.id as string
const note = ref<Note | null>(null)
const showMessages = ref(false)

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
})

async function loadNote() {
  try {
    note.value = await store.fetchNote(Number(noteId))
  } catch (error) {
    showToast('加载笔记失败')
    router.back()
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

// 跳转到复习历史
function navigateToHistory() {
  router.push(`/handbooks/notes/${noteId}/history`)
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

      <!-- 附件列表 -->
      <div class="attachments" v-if="note.attachments?.length">
        <div class="section-title">附件</div>
        <div class="attachment-list">
          <div 
            v-for="file in note.attachments" 
            :key="file.id"
            class="attachment-item"
          >
            <template v-if="file.file_type.startsWith('image/')">
              <div class="image-preview">
                <img :src="file.file_path" :alt="file.file_name">
              </div>
            </template>
            <template v-else>
              <div class="file-info">
                <svg-icon :name="getFileIcon(file.file_type)" />
                <span class="file-name">{{ file.file_name }}</span>
                <van-button 
                  size="small"
                  @click="downloadFile(file)"
                >
                  下载
                </van-button>
              </div>
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
        gap: 12px;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));

        .image-preview {
          img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 8px;
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
    
    // 图标样式
    .van-button__icon {
      margin-right: 4px;
      font-size: 16px;
    }
  }
}
</style> 