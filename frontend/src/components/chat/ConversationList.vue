<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useThemeStore } from '@/stores/theme'
import { showDialog } from 'vant'
import ExportDialog from './ExportDialog.vue'

const chatStore = useChatStore()
const themeStore = useThemeStore()
const editingId = ref<string | null>(null)
const editingTitle = ref('')
const searchKeyword = ref('')
const showExportDialog = ref(false)

function startEditing(conv: { id: string; title: string }) {
  editingId.value = conv.id
  editingTitle.value = conv.title
}

function handleTitleSubmit() {
  if (editingId.value) {
    chatStore.updateConversationTitle(editingId.value, editingTitle.value)
    editingId.value = null
  }
}

function handleTitleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    handleTitleSubmit()
  } else if (event.key === 'Escape') {
    editingId.value = null
  }
}

// 过滤会话列表
const filteredConversations = computed(() => {
  if (!searchKeyword.value) return chatStore.conversations
  
  const keyword = searchKeyword.value.toLowerCase()
  return chatStore.conversations.filter(conv => {
    // 搜索标题
    if (conv.title.toLowerCase().includes(keyword)) return true
    // 搜索消息内容
    return conv.messages.some(msg => 
      msg.content.toLowerCase().includes(keyword)
    )
  })
})

// 显示更多操作菜单
function showMoreActions(conv: Conversation) {
  showDialog({
    title: '会话操作',
    message: '请选择要执行的操作',
    showCancelButton: true,
    confirmButtonText: '导出会话',
    cancelButtonText: '删除会话',
    onConfirm: () => {
      showExportDialog.value = true
    },
    onCancel: () => {
      handleDeleteConversation(conv.id)
    }
  })
}
</script>

<template>
  <div class="conversation-list">
    <div class="header">
      <van-button 
        block 
        class="new-chat-btn"
        @click="chatStore.createNewConversation"
      >
        <template #icon>
          <van-icon name="plus" />
        </template>
        新建会话
      </van-button>
    </div>

    <div class="search-bar">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索会话历史"
        shape="round"
      />
    </div>

    <div class="sessions">
      <div
        v-for="conv in filteredConversations"
        :key="conv.id"
        class="session-item"
        :class="{ active: conv.id === chatStore.currentConversationId }"
        @click="chatStore.currentConversationId = conv.id"
      >
        <div class="session-icon">
          <van-icon name="chat-o" />
        </div>
        <div class="session-info">
          <div class="session-title">{{ conv.title || '新会话' }}</div>
          <div class="session-preview">
            {{ conv.messages[conv.messages.length - 1]?.content.slice(0, 30) || '暂无消息' }}
          </div>
        </div>
        <div class="session-actions">
          <van-button
            size="mini"
            icon="ellipsis"
            @click.stop="showMoreActions(conv)"
          />
        </div>
      </div>
    </div>

    <div class="footer">
      <van-button
        block
        class="theme-toggle"
        @click="themeStore.toggleTheme"
      >
        <template #icon>
          <van-icon :name="themeStore.isDark ? 'sunny-o' : 'moon-o'" />
        </template>
        {{ themeStore.isDark ? '浅色模式' : '深色模式' }}
      </van-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.conversation-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--van-background);
  border-right: 1px solid var(--van-border-color);
}

.header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--van-border-color);
}

.new-chat-btn {
  height: 2.75rem;
  border: 1px solid var(--van-border-color);
  border-radius: var(--radius-md);
  background: var(--van-background);
  color: var(--van-text-color);
  font-size: 0.875rem;
  
  &:hover {
    background: var(--van-active-color);
  }
  
  :deep(.van-icon) {
    font-size: 1rem;
  }
}

.search-bar {
  padding: 0.5rem;
  border-bottom: 1px solid var(--van-border-color);
  
  :deep(.van-search) {
    padding: 0;
    background: transparent;
  }
  
  :deep(.van-search__content) {
    background: var(--van-active-color);
  }
}

.sessions {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-normal);
  
  &:hover {
    background: var(--van-active-color);
    
    .session-actions {
      opacity: 1;
    }
  }
  
  &.active {
    background: var(--van-primary-color-light);
    
    .session-icon {
      color: var(--van-primary-color);
    }
  }
}

.session-icon {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  color: var(--van-text-color-2);
  
  :deep(.van-icon) {
    font-size: 1.25rem;
  }
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--van-text-color);
}

.session-preview {
  font-size: 0.75rem;
  color: var(--van-text-color-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-actions {
  opacity: 0;
  transition: var(--transition-normal);
  
  :deep(.van-button) {
    color: var(--van-text-color-2);
    background: transparent;
    border: none;
    
    &:hover {
      color: var(--van-text-color);
    }
  }
}

.footer {
  padding: 0.75rem;
  border-top: 1px solid var(--van-border-color);
}

.theme-toggle {
  height: 2.75rem;
  border: 1px solid var(--van-border-color);
  border-radius: var(--radius-md);
  background: var(--van-background);
  color: var(--van-text-color);
  font-size: 0.875rem;
  
  &:hover {
    background: var(--van-active-color);
  }
  
  :deep(.van-icon) {
    font-size: 1rem;
  }
}

// 移动端适配
@media (max-width: 768px) {
  .session-actions {
    opacity: 1;
  }
}
</style> 