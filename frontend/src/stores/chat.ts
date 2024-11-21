import { defineStore } from 'pinia'
import { ref } from 'vue'
import { showToast } from 'vant'
import axios from 'axios'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  status?: 'success' | 'error' | 'sending'
}

interface Conversation {
  id: string
  title: string
  lastTime: string
  messages: Message[]
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const currentSession = ref<string>('')
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<string | null>(null)

  // 初始化聊天
  async function initializeChat() {
    try {
      // 如果没有当前会话，创建一个新会话
      if (!currentSession.value) {
        const sessionId = 'new-session-' + Date.now()
        setCurrentSession(sessionId)
      }

      // 如果有持久化的会话数据，加载会话
      if (currentSession.value) {
        const conversation = conversations.value.find(
          conv => conv.id === currentSession.value
        )
        if (conversation) {
          messages.value = conversation.messages
        }
      }

      // 可以添加加载历史会话的 API 调用
      // const response = await axios.get('/api/v1/conversations')
      // conversations.value = response.data

    } catch (error) {
      console.error('初始化聊天失败:', error)
      showToast({
        message: '初始化聊天失败',
        type: 'fail',
        position: 'top'
      })
    }
  }

  // 发送消息
  async function sendMessage(content: string) {
    if (!currentSession.value) return

    const messageId = Date.now().toString()
    const message: Message = {
      id: messageId,
      role: 'user',
      content,
      timestamp: Date.now(),
      status: 'sending'
    }

    try {
      messages.value.push(message)
      updateConversation(currentSession.value, message)

      const response = await axios.post(`/api/v1/chat/${currentSession.value}`, {
        message: content
      })

      // 更新消息状态为成功
      message.status = 'success'

      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.data.message,
        timestamp: Date.now(),
        status: 'success'
      }
      
      messages.value.push(assistantMessage)
      updateConversation(currentSession.value, assistantMessage)
      
    } catch (error) {
      message.status = 'error'
      showToast({
        message: '发送消息失败，请重试',
        type: 'fail',
        position: 'top'
      })
      console.error('发送消息失败:', error)
    } finally {
      isLoading.value = false
    }
  }

  // 更新会话信息
  function updateConversation(sessionId: string, message: Message) {
    const index = conversations.value.findIndex(conv => conv.id === sessionId)
    if (index === -1) {
      conversations.value.push({
        id: sessionId,
        title: message.content.slice(0, 20) + (message.content.length > 20 ? '...' : ''),
        lastTime: new Date().toLocaleString(),
        messages: [message]
      })
    } else {
      const conversation = conversations.value[index]
      conversation.messages.push(message)
      conversation.lastTime = new Date().toLocaleString()
      if (message.role === 'user') {
        conversation.title = message.content.slice(0, 20) + (message.content.length > 20 ? '...' : '')
      }
    }
  }

  function clearMessages() {
    messages.value = []
  }

  function setCurrentSession(sessionId: string) {
    currentSession.value = sessionId
    clearMessages()
  }

  async function updateConversationTitle(id: string, newTitle: string) {
    try {
      const conversation = conversations.value.find(conv => conv.id === id)
      if (conversation) {
        conversation.title = newTitle.trim() || '新对话'
        
        // 可以添加调用后端 API 更新标题的逻辑
      }
    } catch (error) {
      console.error('更新标题失败:', error)
      message.error('更新标题失败')
    }
  }

  // 获取消息预览
  function getMessagePreview(message?: Message) {
    if (!message) return '新会话'
    return message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
  }
  
  // 设置当前会话
  function setCurrentConversation(id: string) {
    currentConversationId.value = id
  }
  
  // 删除会话
  async function deleteConversation(id: string) {
    try {
      // 如果删除的是当前会话，切换到其他会话
      if (currentConversationId.value === id) {
        const otherConv = conversations.value.find(conv => conv.id !== id)
        currentConversationId.value = otherConv?.id || null
      }
      
      conversations.value = conversations.value.filter(conv => conv.id !== id)
      
      // 可以添加调用后端 API 删除会话的逻辑
    } catch (error) {
      console.error('删除会话失败:', error)
      showToast('删除会话失败')
    }
  }

  async function retryMessage(messageId: string) {
    const conversation = conversations.value.find(
      conv => conv.messages.some(msg => msg.id === messageId)
    )
    
    if (!conversation) return
    
    const messageIndex = conversation.messages.findIndex(
      msg => msg.id === messageId
    )
    
    if (messageIndex === -1) return
    
    // 获取需要重试的消息
    const message = conversation.messages[messageIndex]
    
    // 删除之后的所有消息
    conversation.messages = conversation.messages.slice(0, messageIndex)
    
    // 重新发送消息
    await sendMessage(message.content)
  }

  return {
    messages,
    isLoading,
    currentSession,
    conversations,
    currentConversationId,
    initializeChat,
    sendMessage,
    clearMessages,
    setCurrentSession,
    updateConversation,
    updateConversationTitle,
    getMessagePreview,
    setCurrentConversation,
    deleteConversation,
    retryMessage
  }
}, {
  persist: true
})
