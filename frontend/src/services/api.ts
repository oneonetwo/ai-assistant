import { request } from '@/utils/request'

const API_BASE_URL = '/api/v1'

/**
 * 会话管理 API 类
 */
export class ConversationAPI {
  /**
   * 创建新会话
   * @param title - 会话标题
   * @returns Promise<{ session_id: string }>
   */
  static async createConversation(title = '新会话') {
    const response = await request.post(`${API_BASE_URL}/context/conversations`, {
      title
    })
    return response.data
  }

  /**
   * 获取会话信息
   * @param sessionId - 会话ID
   */
  static async getConversation(sessionId: string) {
    const response = await request.get(`${API_BASE_URL}/context/conversations/${sessionId}`)
    return response.data
  }

  /**
   * 获取所有会话
   */
  static async getConversations() {
    const response = await request.get(`${API_BASE_URL}/context/conversations`)
    return response.data
  }

  /**
   * 清除会话上下文
   * @param sessionId - 会话ID
   */
  static async clearContext(sessionId: string) {
    const response = await request.delete(`${API_BASE_URL}/context/conversations/${sessionId}/context`)
    return response.data
  }
}

/**
 * 聊天客户端类
 */
export class ChatClient {
  private sessionId: string
  private baseUrl: string

  constructor(sessionId: string) {
    this.sessionId = sessionId
    this.baseUrl = `${API_BASE_URL}/chat`
  }

  /**
   * 发送消息并获取流式响应
   * @param message - 用户消息
   * @param callbacks - 回调函数集合
   */
  async streamChat(
    message: string,
    callbacks: {
      onStart?: () => void
      onChunk?: (chunk: string, fullText: string) => void
      onEnd?: (fullText: string) => void
      onError?: (error: Error) => void
    } = {}
  ) {
    const { onStart = () => {}, onChunk = () => {}, onEnd = () => {}, onError = () => {} } = callbacks

    const eventSource = new EventSource(
      `${this.baseUrl}/${this.sessionId}/stream`
    )

    let fullText = ''

    // 处理服务器发送的事件
    eventSource.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data)
        
        switch (response.type) {
          case 'start':
            onStart()
            break
            
          case 'chunk':
            fullText += response.data.content
            onChunk(response.data.content, fullText)
            break
            
          case 'end':
            onEnd(response.data.full_text)
            eventSource.close()
            break
            
          case 'error':
            onError(new Error(response.data.message))
            eventSource.close()
            break
        }
      } catch (error) {
        onError(error as Error)
        eventSource.close()
      }
    }

    // 处理连接错误
    eventSource.onerror = (error) => {
      onError(error as Error)
      eventSource.close()
    }

    // 发送用户消息
    try {
      const response = await request.post(`${this.baseUrl}/${this.sessionId}/stream`, {
        message
      })
      return response.data
    } catch (error) {
      eventSource.close()
      onError(error as Error)
    }
  }
} 