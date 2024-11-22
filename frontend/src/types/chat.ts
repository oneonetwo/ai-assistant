export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  status?: 'sending' | 'success' | 'error'
  error?: string
  quote?: Message
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  lastTime: string
  model: string
} 