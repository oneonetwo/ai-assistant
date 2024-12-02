import type { Message } from '@/types/chat'
import { request } from '@/utils/request'

const API_BASE_URL = '/api/v1'

/**
 * 会话管理 API 类
 */
export class ConversationAPI {
  /**
   * 创建新会话
   * @param name - 会话标题
   * @returns Promise<{ session_id: string }>
   */
  static async createConversation(name = '新会话') {
    const response = await request.post(`${API_BASE_URL}/context/conversations`, {
      name: name
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
   * 清除会话上
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

  constructor(sessionId?: string) {
    this.sessionId = sessionId || ''
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

  async streamAnalyze(
    messages: Pick<Message, 'role' | 'content' | 'id'>[],
    systemPrompt: string,
    callbacks: {
      onStart?: () => void
      onChunk?: (content: string, section: string, fullText: string) => void
      onEnd?: () => void
      onError?: (error: Error) => void
    } = {}
  ) {
    try {
      // 初始化分析
      const response = await request.post(`${this.baseUrl}/analyze/stream/init`, {
        messages,
        system_prompt: systemPrompt
      })

      // 建立 SSE 连接
      const url = new URL(`${window.location.origin}/api${this.baseUrl}/analyze/stream/${response.session_id}`)
      const eventSource = new EventSource(url.toString())
      let fullText = ''
      eventSource.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data)
          
          switch (response.type) {
            case 'start':
              callbacks.onStart?.()
              break
              
            case 'chunk':
              callbacks.onChunk?.(
                response.data.content, 
                response.data.section,
                response.data.full_text
              )
              break
              
            case 'end':
              callbacks.onEnd?.()
              eventSource.close()
              break
              
            case 'error':
              throw new Error(response.data.message)
          }
        } catch (error) {
          eventSource.close()
          callbacks.onError?.(error as Error)
        }
      }

      eventSource.onerror = (error) => {
        eventSource.close()
        callbacks.onError?.(error as Error)
      }

    } catch (error) {
      callbacks.onError?.(error as Error)
    }
  }
}

/**
 * 聊天相关 API 类
 */
export class ChatAPI {
  /**
   * 发送带图片的消息并获取AI分析（流式响应）
   */
  static async streamImageChat(
    sessionId: string,
    message: string,
    imageUrl: string,
    callbacks: {
      onStart?: () => void
      onChunk?: (chunk: string, fullText: string) => void
      onEnd?: (fullText: string) => void
      onError?: (error: Error) => void
      signal?: AbortSignal
    } = {},
    options: {
      systemPrompt?: string
      extractText?: boolean
    } = {}
  ) {
    try {
      // 首先发送 POST 请求初始化流
      await request.post(`${API_BASE_URL}/chat/${sessionId}/image/stream`, {
        message,
        image: imageUrl,
        system_prompt: options.systemPrompt || '你是一个专业的图像分析助手',
        extract_text: options.extractText || false
      })

      // 然后建立 SSE 连接
      const url = new URL(
        `${window.location.origin}/api${API_BASE_URL}/chat/${sessionId}/image/stream`
      )
      
      const eventSource = new EventSource(url.toString())
      let fullText = ''

      eventSource.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data)
          
          switch (response.type) {
            case 'start':
              callbacks.onStart?.()
              break
              
            case 'chunk':
              fullText += response.data.content
              callbacks.onChunk?.(response.data.content, fullText)
              break
              
            case 'end':
              callbacks.onEnd?.(fullText)
              eventSource.close()
              break
              
            case 'error':
              throw new Error(response.data.message)
          }
        } catch (error) {
          eventSource.close()
          callbacks.onError?.(error as Error)
        }
      }

      eventSource.onerror = (error) => {
        eventSource.close()
        callbacks.onError?.(error as Error)
      }

    } catch (error) {
      callbacks.onError?.(error as Error)
    }
  }

  /**
   * 发送带文件的消息并获取AI分析（流式响应）
   */
  static async streamFileChat(
    sessionId: string,
    message: string,
    fileUrl: string,
    fileName: string,
    fileType: string,
    callbacks: {
      onStart?: () => void
      onChunk?: (chunk: string, fullText: string) => void
      onEnd?: (fullText: string) => void
      onError?: (error: Error) => void
      signal?: AbortSignal
    } = {},
    options: {
      systemPrompt?: string
    } = {}
  ) {
    try {
      // 首先发送 POST 请求初始化流
      await request.post(`${API_BASE_URL}/chat/${sessionId}/file/stream`, {
        message,
        file: fileUrl,
        file_name: fileName,
        file_type: fileType,
        system_prompt: options.systemPrompt || '你是一个专业的文件分析助手'
      })

      // 然后建立 SSE 连接
      const url = new URL(
        `${window.location.origin}/api${API_BASE_URL}/chat/${sessionId}/file/stream`
      )
      
      const eventSource = new EventSource(url.toString())
      let fullText = ''

      eventSource.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data)
          
          switch (response.type) {
            case 'start':
              callbacks.onStart?.()
              break
              
            case 'chunk':
              fullText += response.data.content
              callbacks.onChunk?.(response.data.content, fullText)
              break
              
            case 'end':
              callbacks.onEnd?.(fullText)
              eventSource.close()
              break
              
            case 'error':
              throw new Error(response.data.message)
          }
        } catch (error) {
          eventSource.close()
          callbacks.onError?.(error as Error)
        }
      }

      eventSource.onerror = (error) => {
        eventSource.close()
        callbacks.onError?.(error as Error)
      }

    } catch (error) {
      callbacks.onError?.(error as Error)
    }
  }
} 