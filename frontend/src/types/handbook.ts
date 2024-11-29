export interface Category {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface Handbook {
  id: number
  name: string
  category_id: number
  created_at: string
  updated_at: string
}

export interface Tag {
  id: number
  name: string
}

export interface Attachment {
  file_id: string
  original_name: string
  file_path: string
  file_type: string
  mime_type: string
  file_size: number
}

export type NotePriority = 'low' | 'medium' | 'high'
export type NoteStatus = '待复习' | '复习中' | '已完成'

export interface Note {
  id: number
  title: string
  content: string
  handbook_id: number
  tags: Tag[]
  priority: NotePriority
  times: number
  status: NoteStatus
  is_shared: boolean
  attachments: Attachment[]
  created_at: string
  updated_at: string
}

export interface CreateNoteData {
  title: string
  content: string
  handbook_id: number
  tags: string[]
  priority: NotePriority
  status: NoteStatus
  is_shared: boolean
  attachments?: {
    url: string
    file_name: string
  }[]
}

export interface UpdateNoteData {
  title?: string
  content?: string
  tags?: string[]
  priority?: NotePriority
  status?: NoteStatus
  is_shared?: boolean
} 