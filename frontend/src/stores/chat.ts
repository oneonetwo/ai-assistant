import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { showToast, showDialog } from 'vant'
import { ConversationAPI, ChatClient, ChatAPI } from '@/services/api'
import type { Message, Conversation, MessageStatus } from '@/types/chat'
import { generateUUID } from '@/utils/generateUUID'
import { uploadToOSS } from '@/utils/oss'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const currentConversation = computed(() => {
    return conversations.value.find(conv => conv.id === currentConversationId.value)
  })

  const currentMessages = computed(() => {
    return currentConversation.value?.messages || []
  })

  // 添加文件相关状态
  const uploadingFiles = ref<Map<string, {
    progress: number
    controller: AbortController
  }>>(new Map())

  // 初始化聊天
  async function initializeChat() {
    try {
      isLoading.value = true
      const data = await ConversationAPI.getConversations()
      conversations.value = data.map((conv: any) => ({
        id: conv.session_id,
        name: conv.name || '新会话',
        messages: conv.messages || [],
        lastTime: conv.created_at,
        model: conv.model || 'gpt-3.5-turbo'
      }))
      
      if (conversations.value.length > 0) {
        currentConversationId.value = conversations.value[0].id
      } else {
        // await createNewConversation()
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
  async function createNewConversation(name = '新会话') {
    try {
      isLoading.value = true
      const { session_id } = await ConversationAPI.createConversation(name)
      
      const newConversation: Conversation = {
        id: session_id,
        name,
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
    console.log('sendMessage', content, options)
    console.log('currentConversation.value', currentConversation.value)
    console.log('currentConversationId.value', currentConversationId.value)
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
        id: generateUUID(),
        parent_message_id: userMessage.id,
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
          console.log('start >>>>>>>>>>>')

          userMessage.status = 'success'
        },
        onChunk: (chunk: string) => {
          updateMessageContent(currentConversationId.value!, assistantMessage.id, chunk)
        },
        onEnd: () => {
          console.log('onEnd>>>>>>>>>>>')
          // 更新消息状态
          assistantMessage.status = 'success'
          // 更新会话时间
          conversation.lastTime = new Date().toISOString()
        },
        onError: (error: Error) => {
          console.log('onError>>>>>>>>>>>', error)
          assistantMessage.status = 'error'
          assistantMessage.error = error.message
          throw error
        }
      })

    } catch (error: any) {
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
        name: '清空会话',
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
  async function renameConversation(id: string, name: string) {
    const conversation = conversations.value.find(conv => conv.id === id)
    if (!conversation) return

    const originalName = conversation.name

    try {
      // 乐观更新
      conversation.name = name
      
      // 调用重命名API
      await ConversationAPI.updateConversation(id, name)
      
      showToast({
        type: 'success',
        message: '重命名成功'
      })
    } catch (error) {
      // 发生错误时恢复原名称
      conversation.name = originalName
      
      showToast({
        type: 'fail',
        message: '重命名失败'
      })
      
      throw error
    }
  }

  /**
   * 更新会话信息
   * @param id - 会话ID
   * @param conversation - 服务器返回的会话数据
   */
  function updateConversation(id: string, conversation: {
    session_id?: string
    name?: string
    messages?: any[]
    created_at?: string
    model?: string
  }) {
    try {
      const index = conversations.value.findIndex(conv => conv.id === id)
      if (index === -1) {
        console.warn(`Conversation with id ${id} not found`)
        return
      }

      // 转换服务器数据格式为本地格式
      const updatedConversation = {
        id: conversation.session_id || conversations.value[index].id,
        name: conversation.name || conversations.value[index].name,
        messages: conversation.messages?.map(msg => ({
          id: msg.id || Date.now().toString(),
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.timestamp || Date.now(),
          status: msg.status || 'success',
          error: msg.error,
          quote: msg.quote
        })) || conversations.value[index].messages,
        lastTime: conversation.created_at || conversations.value[index].lastTime,
        model: conversation.model || conversations.value[index].model
      }

      // 更新会话
      conversations.value[index] = {
        ...conversations.value[index],
        ...updatedConversation
      }

      // 如果更新的是当前会话，确保 currentConversationId 也是最新的
      if (currentConversationId.value === id && conversation.session_id) {
        currentConversationId.value = conversation.session_id
      }
    } catch (error) {
      console.error('Failed to update conversation:', error)
      showToast({
        type: 'fail',
        message: '更新会话失败'
      })
    }
  }

  // 新建会话
  async function createNewChat() {
    const conversation: Conversation = {
      id: Date.now().toString(),
      name: '新会话',
      messages: [],
      lastTime: new Date().toISOString()
    }
    
    conversations.value.unshift(conversation)
    currentConversationId.value = conversation.id
  }

  // 添加新的 action
  function updateMessageContent(conversationId: string, messageId: string, content: string) {
    const conversation = conversations.value.find(conv => conv.id === conversationId)
    if (!conversation) return

    const messageIndex = conversation.messages.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) return

    // 创建新的消息数组并更新内容
    conversation.messages = conversation.messages.map((msg, index) => 
      index === messageIndex 
        ? { ...msg, content: msg.content + content }
        : msg
    )
  }

  // 发送带文件的消息（支持图片和其他文件）
  async function sendMessageWithFile(
    content: string,
    file: File,
    options: {
      onProgress?: (progress: number) => void
      signal?: AbortSignal
      systemPrompt?: string
      extractText?: boolean
    } = {}
  ) {
    if (!currentConversationId.value) {
      throw new Error('未选择会话')
    }

    const conversation = currentConversation.value
    if (!conversation) return

    const messageId = generateUUID()
    const isImage = file.type.startsWith('image/')

    try {
      // 创建用户消息
      const userMessage: Message = {
        id: messageId,
        role: 'user',
        content,
        timestamp: Date.now(),
        status: 'sending',
        file: {
          name: file.name,
          type: file.type,
          size: file.size,
          url: URL.createObjectURL(file)
        }
      }
      
      // 添加到上传队列
      uploadingFiles.value.set(messageId, {
        progress: 0,
        controller: new AbortController()
      })
      
      conversation.messages.push(userMessage)

      // 先上传到 OSS
      const fileUrl = await uploadToOSS(file, {
        onProgress: (progress) => {
          updateFileProgress(messageId, progress)
          options.onProgress?.(progress)
        },
        signal: options.signal
      })

      // 更新文件 URL
      userMessage.file!.url = fileUrl

      // 根据文件类型调用不同的 API
      const response = isImage 
        ? await ChatAPI.sendImageMessage(
            currentConversationId.value,
            content,
            fileUrl,
            {
              systemPrompt: options.systemPrompt,
              extractText: options.extractText
            }
          )
        : await ChatAPI.sendFileMessage(
            currentConversationId.value,
            content,
            fileUrl,
            file.name,
            file.type,
            {
              systemPrompt: options.systemPrompt
            }
          )

      // 更新消息状态
      userMessage.status = 'success'
      updateConversation(currentConversationId.value, {
        messages: [...conversation.messages, response.data]
      })

    } catch (error) {
      console.error(`发送${isImage ? '图片' : '文件'}消息失败:`, error)
      const message = error.message === '上传已取消' 
        ? '上传已取消' 
        : `发送${isImage ? '图片' : '文件'}消息失败`
      showToast({
        type: 'fail',
        message
      })
      throw error
    } finally {
      // 清理上传状态
      uploadingFiles.value.delete(messageId)
    }
  }

  // 添加文件上传进度更新方法
  function updateFileProgress(messageId: string, progress: number) {
    const fileUpload = uploadingFiles.value.get(messageId)
    if (fileUpload) {
      fileUpload.progress = progress
    }
  }

  // 添加取消上传方法
  function cancelFileUpload(messageId: string) {
    const fileUpload = uploadingFiles.value.get(messageId)
    if (fileUpload) {
      fileUpload.controller.abort()
      uploadingFiles.value.delete(messageId)
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
    renameConversation,
    updateConversation,
    createNewChat,
    sendMessageWithFile,
    updateFileProgress,
    cancelFileUpload
  }
})