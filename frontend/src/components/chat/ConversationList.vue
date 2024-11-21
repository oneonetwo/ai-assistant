<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useThemeStore } from '@/stores/theme'
import { showDialog } from 'vant'
import ExportDialog from './ExportDialog.vue'

const chatStore = useChatStore()
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
    <!-- 搜索框 -->
    <div class="search-bar">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索会话"
        shape="round"
      />
    </div>
    
    <!-- 新建会话按钮 -->
    <div class="new-chat" @click="createNewSession">
      <van-button block type="primary" size="small">
        新建会话
      </van-button>
    </div>

    <!-- 会话列表 -->
    <div class="sessions">
      <div
        v-for="session in filteredConversations"
        :key="session.id"
        class="session-item"
        :class="{ active: session.id === currentSession }"
        @click="selectSession(session.id)"
      >
        <span class="session-title">{{ session.title || '新会话' }}</span>
        <span class="session-time">{{ session.lastTime }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.conversation-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--van-background-2);
}

.new-chat {
  padding: var(--van-padding-sm);
  border-bottom: 1px solid var(--van-border-color);
}

.sessions {
  flex: 1;
  overflow-y: auto;
  padding: var(--van-padding-xs);
}

.session-item {
  display: flex;
  flex-direction: column;
  padding: var(--van-padding-sm);
  margin-bottom: var(--van-padding-xs);
  border-radius: var(--van-radius-md);
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--van-active-color);
  }

  &.active {
    background-color: var(--van-primary-color);
    color: var(--van-white);
  }
}

.session-title {
  font-size: var(--van-font-size-md);
  margin-bottom: var(--van-padding-xs);
}

.session-time {
  font-size: var(--van-font-size-sm);
  color: var(--van-text-color-2);

  .active & {
    color: var(--van-white);
    opacity: 0.8;
  }
}

.title-input {
  width: 100%;
  background: transparent;
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 4px 8px;
  color: var(--text-color);
  font-size: 14px;
  
  &:focus {
    outline: none;
  }
}

.action-buttons {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  
  button {
    padding: 4px;
    background: transparent;
    border: none;
    color: var(--van-gray-5);
    cursor: pointer;
    
    &:hover {
      color: var(--text-color);
    }
  }
}

.conversation-item {
  &:hover .action-buttons,
  &.active .action-buttons {
    opacity: 1;
  }
  
  &.editing {
    background: rgba(255, 255, 255, 0.1);
    
    .action-buttons {
      display: none;
    }
  }
}

@media (max-width: 768px) {
  .action-buttons {
    opacity: 1;
  }
}
</style> 