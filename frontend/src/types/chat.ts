export interface Message {
  id: string
  role: 'user' | 'assistant'
  parent_message_id?: string
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