import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Handbook, Note, Tag, Attachment } from '@/types/handbook'
import { request } from '@/utils/request'

export const useHandbookStore = defineStore('handbook', () => {
  const handbooks = ref<Handbook[]>([])
  const currentHandbook = ref<Handbook | null>(null)
  const notes = ref<Note[]>([])
  const tags = ref<Tag[]>([])
  
  // 手册管理
  async function fetchHandbooks() {
    const response = await request.get('/api/v1/handbooks')
    handbooks.value = response.data
  }

  async function createHandbook(data: Partial<Handbook>) {
    const response = await request.post('/api/v1/handbooks', data)
    handbooks.value.unshift(response.data)
    return response.data
  }

  async function updateHandbook(id: string, data: Partial<Handbook>) {
    const response = await request.patch(`/api/v1/handbooks/${id}`, data)
    const index = handbooks.value.findIndex(h => h.id === id)
    if (index !== -1) {
      handbooks.value[index] = response.data
    }
    return response.data
  }

  async function deleteHandbook(id: string) {
    await request.delete(`/api/v1/handbooks/${id}`)
    handbooks.value = handbooks.value.filter(h => h.id !== id)
  }

  // 笔记管理
  async function fetchNotes(handbookId: string) {
    const response = await request.get(`/api/v1/handbooks/${handbookId}/notes`)
    notes.value = response.data
  }

  async function createNote(handbookId: string, data: Partial<Note>) {
    const response = await request.post(`/api/v1/handbooks/${handbookId}/notes`, data)
    notes.value.unshift(response.data)
    return response.data
  }

  async function updateNote(id: string, data: Partial<Note>) {
    const response = await request.patch(`/api/v1/notes/${id}`, data)
    const index = notes.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notes.value[index] = response.data
    }
    return response.data
  }

  async function deleteNote(id: string) {
    await request.delete(`/api/v1/notes/${id}`)
    notes.value = notes.value.filter(n => n.id !== id)
  }

  // 标签管理
  async function fetchTags() {
    const response = await request.get('/api/v1/tags')
    tags.value = response.data
  }

  async function createTag(name: string) {
    const response = await request.post('/api/v1/tags', { name })
    tags.value.push(response.data)
    return response.data
  }

  async function deleteTag(id: string) {
    await request.delete(`/api/v1/tags/${id}`)
    tags.value = tags.value.filter(t => t.id !== id)
  }

  // 附件管理
  async function uploadAttachment(noteId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await request.post(`/api/v1/attachments/notes/${noteId}`, formData)
    return response.data
  }

  async function deleteAttachment(id: string) {
    await request.delete(`/api/v1/attachments/${id}`)
  }

  return {
    handbooks,
    currentHandbook,
    notes,
    tags,
    fetchHandbooks,
    createHandbook,
    updateHandbook,
    deleteHandbook,
    fetchNotes,
    createNote,
    updateNote,
    deleteNote,
    fetchTags,
    createTag,
    deleteTag,
    uploadAttachment,
    deleteAttachment
  }
}) 