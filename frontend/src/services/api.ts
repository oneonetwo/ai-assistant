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
    return response
  }

  /**
   * 获取会话信息
   * @param sessionId - 会话ID
   */
  static async getConversation(sessionId: string) {
    const response = await request.get(`${API_BASE_URL}/context/conversations/${sessionId}`)
    return response
  }

  /**
   * 获取所有会话
   */
  static async getConversations() {
    const response = await request.get(`${API_BASE_URL}/context/conversations`)
    return response
  }

  /**
   * 删除会话
   * @param sessionId - 会话ID
   */
  static async deleteConversation(sessionId: string) {
    const response = await request.delete(`${API_BASE_URL}/context/conversations/${sessionId}`)
    return response
  }

  /**
   * 清除会话上下文
   * @param sessionId - 会话ID
   */
  static async clearContext(sessionId: string) {
    const response = await request.delete(`${API_BASE_URL}/context/conversations/${sessionId}/context`)
    return response
  }

  /**
   * 更新会话信息
   * @param sessionId - 会话ID
   * @param name - 新的会话标题
   */
  static async updateConversation(sessionId: string, name: string) {
    const response = await request.patch(`${API_BASE_URL}/context/conversations/${sessionId}`, {
      name
    })
    return response
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
  ): Promise<void> {
    const { onStart = () => {}, onChunk = () => {}, onEnd = () => {}, onError = () => {} } = callbacks

    try {
      // 首先发送 POST 请求初始化流
      await request.post(`${this.baseUrl}/${this.sessionId}/stream`, {
        message
      })

      // 然后建立 SSE 连接
      const url = new URL(
        `${window.location.origin}/api${this.baseUrl}/${this.sessionId}/stream`
      )
      
      const eventSource = new EventSource(url.toString())
      let fullText = ''

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
              onEnd(fullText)
              eventSource.close()
              break
              
            case 'error':
              throw new Error(response.data.message)
          }
        } catch (error) {
          eventSource.close()
          onError(error as Error)
        }
      }

      eventSource.onerror = (error) => {
        eventSource.close()
        onError(error as Error)
      }

    } catch (error) {
      onError(error as Error)
    }
  }
} 