<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import { showDialog, showToast } from 'vant'

const chatStore = useChatStore()
const { conversations, currentConversationId } = storeToRefs(chatStore)

// 格式化预览文本
function getPreviewText(messages: any[]) {
  if (!messages?.length) return '暂无消息'
  const lastMessage = messages[messages.length - 1]
  return lastMessage.content.slice(0, 50) + (lastMessage.content.length > 50 ? '...' : '')
}

// 处理会话点击
async function handleSessionClick(conv: { id: string }) {
  try {
    chatStore.currentConversationId = conv.id
  } catch (error) {
    showToast('加载会话失败')
  }
}

// 删除会话
async function handleDeleteConversation(conv: { id: string }) {
  try {
    await showDialog({
      title: '删除会话',
      message: '确定要删除这个会话吗？',
      showCancelButton: true
    })
    
    await chatStore.deleteConversation(conv.id)
    showToast('删除成功')
  } catch (error) {
    // 用户取消或删除失败
  }
}

// 重命名会话
async function handleRenameConversation(conv: { id: string, name: string }) {
  const newName = window.prompt('请输入新的会话名称:', conv.name)
  if (!newName || newName === conv.name) return
  
  try {
    await chatStore.renameConversation(conv.id, newName)
  } catch (error) {
    showToast({
      type: 'fail',
      message: '重命名失败'
    })
  }
}
</script>

<template>
  <div class="conversation-list">
    <div v-for="conv in conversations" 
      :key="conv.id"
      class="session-item"
      :class="{ active: conv.id === currentConversationId }"
      @click="handleSessionClick(conv)"
    >
      <div class="session-content">
        <div class="session-title">{{ conv.name || '新会话' }}</div>
        <div class="session-preview">{{ getPreviewText(conv.messages) }}</div>
      </div>
      
      <div class="session-actions">
        <van-button 
          size="mini"
          icon="edit"
          @click.stop="handleRenameConversation(conv)"
        />
        <van-button
          size="mini"
          icon="delete"
          @click.stop="handleDeleteConversation(conv)"
        />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.conversation-list {
  padding: 8px;

  .session-item {
    display: flex;
    align-items: center;
    padding: 12px;
    margin-bottom: 4px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background: var(--van-active-color);
    }
    
    &.active {
      background: var(--van-active-color);
    }
    
    .session-content {
      flex: 1;
      min-width: 0;
      
      .session-title {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 4px;
        @include text-ellipsis;
      }
      
      .session-preview {
        font-size: 12px;
        color: var(--van-text-color-2);
        @include text-ellipsis;
      }
    }
    
    .session-actions {
      display: flex;
      gap: 4px;
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .session-actions {
      opacity: 1;
    }
  }
}
</style> 