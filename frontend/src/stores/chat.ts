import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { showToast, showDialog } from 'vant'
import { ConversationAPI, ChatClient } from '@/services/api'
import type { Message, Conversation, MessageStatus } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const currentConversation = computed(() => 
    conversations.value.find(conv => conv.id === currentConversationId.value)
  )

  const currentMessages = computed(() => 
    currentConversation.value?.messages || []
  )

  // 初始化聊天
  async function initializeChat() {
    try {
      isLoading.value = true
      const data = await ConversationAPI.getConversations()
      console.log('data', data)
      conversations.value = data.map((conv: any) => ({
        id: conv.session_id,
        title: conv.title || '新会话',
        messages: conv.messages || [],
        lastTime: conv.created_at,
        model: conv.model || 'gpt-3.5-turbo'
      }))
      
      if (conversations.value.length > 0) {
        currentConversationId.value = conversations.value[0].id
      } else {
        await createNewConversation()
      }
    } catch (error) {
      showToast({
        type: 'fail',
        message: '初始化失败'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 创建新会话
  async function createNewConversation(title = '新会话') {
    try {
      isLoading.value = true
      const { session_id } = await ConversationAPI.createConversation(title)
      
      const newConversation: Conversation = {
        id: session_id,
        title,
        messages: [],
        lastTime: new Date().toISOString(),
        model: 'gpt-3.5-turbo'
      }
      
      conversations.value.unshift(newConversation)
      currentConversationId.value = newConversation.id
      
      return session_id
    } catch (error) {
      showToast({
        type: 'fail',
        message: '创建会话失败'
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 发送消息
  async function sendMessage(content: string, options: {
    quote?: Message
    retry?: boolean
    messageId?: string
  } = {}) {
    if (!currentConversationId.value) {
      throw new Error('未选择会话')
    }

    const conversation = currentConversation.value
    if (!conversation) return

    const abortController = new AbortController()
    let tempMessageId = options.messageId || Date.now().toString()

    try {
      // 添加用户消息
      const userMessage: Message = {
        id: tempMessageId,
        role: 'user',
        content,
        timestamp: Date.now(),
        status: 'sending',
        quote: options.quote
      }
      
      if (!options.retry) {
        conversation.messages.push(userMessage)
      }

      // 创建助手消息占位
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        status: 'sending'
      }
      
      conversation.messages.push(assistantMessage)

      // 创建聊天客户端
      const chatClient = new ChatClient(currentConversationId.value)
      
      // 发送消息并处理流式响应
      await chatClient.streamChat(content, {
        signal: abortController.signal,
        onStart: () => {
          userMessage.status = 'success'
        },
        onChunk: (chunk, fullText) => {
          assistantMessage.content = fullText
        },
        onEnd: (fullText) => {
          assistantMessage.status = 'success'
          conversation.lastTime = new Date().toISOString()
        },
        onError: (error) => {
          assistantMessage.status = 'error'
          assistantMessage.error = error.message
          throw error
        }
      })

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('请求已取消')
        return
      }

      showToast({
        type: 'fail',
        message: error.message || '发送失败'
      })
      
      // 更新消息状态
      const failedMessage = conversation.messages.find(msg => msg.id === tempMessageId)
      if (failedMessage) {
        failedMessage.status = 'error'
        failedMessage.error = error.message
      }
    }

    return {
      abort: () => abortController.abort()
    }
  }

  // 重试消息
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
    await sendMessage(message.content, {
      retry: true,
      messageId: message.id,
      quote: message.quote
    })
  }

  // 删除会话
  async function deleteConversation(id: string) {
    try {
      await showDialog({
        title: '删除会话',
        message: '确定要删除这个会话吗？',
        showCancelButton: true
      })

      // 如果删除的是当前会话，切换到其他会话
      if (currentConversationId.value === id) {
        const otherConv = conversations.value.find(conv => conv.id !== id)
        currentConversationId.value = otherConv?.id || null
      }
      
      conversations.value = conversations.value.filter(conv => conv.id !== id)
      
      await ConversationAPI.deleteConversation(id)
      
      showToast({
        type: 'success',
        message: '删除成功'
      })
    } catch (error) {
      if (error.cancel) return
      
      showToast({
        type: 'fail',
        message: '删除失败'
      })
    }
  }

  // 清空会话
  async function clearConversation(id: string) {
    try {
      await showDialog({
        title: '清空会话',
        message: '确定要清空这个会话的所有消息吗？',
        showCancelButton: true
      })

      const conversation = conversations.value.find(conv => conv.id === id)
      if (conversation) {
        conversation.messages = []
      }
      
      await ConversationAPI.clearContext(id)
      
      showToast({
        type: 'success',
        message: '清空成功'
      })
    } catch (error) {
      if (error.cancel) return
      
      showToast({
        type: 'fail',
        message: '清空失败'
      })
    }
  }

  // 重命名会话
  async function renameConversation(id: string, title: string) {
    const conversation = conversations.value.find(conv => conv.id === id)
    if (conversation) {
      conversation.title = title
      // TODO: 调用重命名 API
    }
  }

  return {
    conversations,
    currentConversationId,
    currentConversation,
    currentMessages,
    isLoading,
    error,
    initializeChat,
    createNewConversation,
    sendMessage,
    retryMessage,
    deleteConversation,
    clearConversation,
    renameConversation
  }
})