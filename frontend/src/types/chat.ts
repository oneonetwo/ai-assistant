export interface FileInfo {
  original_name: string
  file_type: string
  file_path: string
  file_size: number
  uploadProgress?: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  parent_message_id?: string
  content: string
  timestamp: number
  status?: 'sending' | 'success' | 'error'
  error?: string
  quote?: Message
  file?: FileInfo
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  lastTime: string
  model: string
} 