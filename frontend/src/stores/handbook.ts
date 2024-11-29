import { defineStore } from 'pinia'
import { ref } from 'vue'
import { HandbookAPI } from '@/services/handbookService'
import { NoteAPI } from '@/services/noteService'
import type { Category, Handbook, Note, Tag, CreateNoteData, UpdateNoteData } from '@/types/handbook'

interface Handbook {
  id: number
  name: string
  category_id: number
  created_at: string
  updated_at: string
}

export const useHandbookStore = defineStore('handbook', () => {
  // 状态
  const handbooks = ref<Handbook[]>([])
  const categories = ref<Category[]>([])
  const currentHandbook = ref<Handbook | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const notes = ref<Note[]>([])
  const currentNote = ref<Note | null>(null)
  const tags = ref<Tag[]>([])

  // 分类管理
  async function fetchCategories() {
    try {
      isLoading.value = true
      const response = await HandbookAPI.getCategories()
      categories.value = response
    } catch (err) {
      error.value = '获取分类失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createCategory(name: string) {
    try {
      isLoading.value = true
      const response = await HandbookAPI.createCategory(name)
      categories.value.unshift(response)
      return response
    } catch (err) {
      error.value = '创建分类失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 手册管理
  async function fetchHandbooks(categoryId?: number) {
    try {
      isLoading.value = true
      const response = await HandbookAPI.getHandbooks(categoryId)
      handbooks.value = response
    } catch (err) {
      error.value = '获取手册列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function getHandbook(id: number) {
    try {
      isLoading.value = true
      const response = await HandbookAPI.getHandbook(id)
      currentHandbook.value = response
      return response
    } catch (err) {
      error.value = '获取手册详情失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createHandbook(data: { name: string; category_id: number }) {
    try {
      isLoading.value = true
      const response = await HandbookAPI.createHandbook(data.name, data.category_id)
      handbooks.value.unshift(response)
      return response
    } catch (err) {
      error.value = '创建手册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateHandbook(id: number, data: { name?: string; category_id?: number }) {
    try {
      isLoading.value = true
      const response = await HandbookAPI.updateHandbook(id, data)
      const index = handbooks.value.findIndex(h => h.id === id)
      if (index !== -1) {
        handbooks.value[index] = response
      }
      if (currentHandbook.value?.id === id) {
        currentHandbook.value = response
      }
      return response
    } catch (err) {
      error.value = '更新手册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteHandbook(id: number) {
    try {
      isLoading.value = true
      await HandbookAPI.deleteHandbook(id)
      handbooks.value = handbooks.value.filter(h => h.id !== id)
      if (currentHandbook.value?.id === id) {
        currentHandbook.value = null
      }
    } catch (err) {
      error.value = '删除手册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 笔记管理
  async function fetchNotes(handbookId?: number, tag?: string) {
    try {
      isLoading.value = true
      const response = await NoteAPI.getNotes({ handbook_id: handbookId, tag })
      notes.value = response
    } catch (err) {
      error.value = '获取笔记列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchNote(noteId: number) {
    try {
      isLoading.value = true
      const response = await NoteAPI.getNote(noteId)
      currentNote.value = response
      return response
    } catch (err) {
      error.value = '获取笔记详情失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createNote(data: CreateNoteData) {
    try {
      isLoading.value = true
      const response = await NoteAPI.createNote(data)
      notes.value.unshift(response)
      return response
    } catch (err) {
      error.value = '创建笔记失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateNote(noteId: number, data: UpdateNoteData) {
    try {
      isLoading.value = true
      const response = await NoteAPI.updateNote(noteId, data)
      const index = notes.value.findIndex(n => n.id === noteId)
      if (index !== -1) {
        notes.value[index] = response
      }
      if (currentNote.value?.id === noteId) {
        currentNote.value = response
      }
      return response
    } catch (err) {
      error.value = '更新笔记失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteNote(noteId: number) {
    try {
      isLoading.value = true
      await NoteAPI.deleteNote(noteId)
      notes.value = notes.value.filter(n => n.id !== noteId)
      if (currentNote.value?.id === noteId) {
        currentNote.value = null
      }
    } catch (err) {
      error.value = '删除笔记失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTags() {
    try {
      isLoading.value = true
      const response = await NoteAPI.getTags()
      tags.value = response
    } catch (err) {
      error.value = '获取标签失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 标签管理
  async function createTag(name: string) {
    try {
      isLoading.value = true
      const response = await NoteAPI.createTag(name)
      tags.value.unshift(response)
      return response
    } catch (err) {
      error.value = '创建标签失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateTag(tagId: number, name: string) {
    try {
      isLoading.value = true
      const response = await NoteAPI.updateTag(tagId, name)
      const index = tags.value.findIndex(t => t.id === tagId)
      if (index !== -1) {
        tags.value[index] = response
      }
      return response
    } catch (err) {
      error.value = '更新标签失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteTag(tagId: number) {
    try {
      isLoading.value = true
      await NoteAPI.deleteTag(tagId)
      tags.value = tags.value.filter(t => t.id !== tagId)
    } catch (err) {
      error.value = '删除标签失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function mergeTags(sourceTagId: number, targetTagId: number) {
    try {
      isLoading.value = true
      await NoteAPI.mergeTags(sourceTagId, targetTagId)
      // 更新标签列表
      await fetchTags()
      // 更新笔记列表中的标签
      if (notes.value.length) {
        await fetchNotes()
      }
    } catch (err) {
      error.value = '合并标签失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 清除状态
  function reset() {
    handbooks.value = []
    categories.value = []
    currentHandbook.value = null
    isLoading.value = false
    error.value = null
    notes.value = []
    currentNote.value = null
    tags.value = []
  }

  return {
    // 状态
    handbooks,
    categories,
    currentHandbook,
    isLoading,
    error,
    notes,
    currentNote,
    tags,

    // 分类操作
    fetchCategories,
    createCategory,

    // 手册操作
    fetchHandbooks,
    getHandbook,
    createHandbook,
    updateHandbook,
    deleteHandbook,

    // 笔记操作
    fetchNotes,
    fetchNote,
    createNote,
    updateNote,
    deleteNote,
    fetchTags,

    // 标签操作
    createTag,
    updateTag,
    deleteTag,
    mergeTags,

    // 工具方法
    reset
  }
}) 