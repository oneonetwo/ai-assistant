import { request } from '@/utils/request'
import type { Note, CreateNoteData, UpdateNoteData, Tag } from '@/types/handbook'

const API_BASE_URL = '/api/v1'

/**
 * 笔记管理 API 类
 */
export class NoteAPI {
  /**
   * 创建笔记
   */
  static async createNote(data: CreateNoteData): Promise<Note> {
    const response = await request.post(`${API_BASE_URL}/notes`, data)
    return response
  }

  /**
   * 获取笔记列表
   */
  static async getNotes(params?: { handbook_id?: number; tag?: string }): Promise<Note[]> {
    const response = await request.get(`${API_BASE_URL}/notes`, { params })
    return response
  }

  /**
   * 获取单个笔记
   */
  static async getNote(noteId: number): Promise<Note> {
    const response = await request.get(`${API_BASE_URL}/notes/${noteId}`)
    return response
  }

  /**
   * 更新笔记
   */
  static async updateNote(noteId: number, data: UpdateNoteData): Promise<Note> {
    const response = await request.patch(`${API_BASE_URL}/notes/${noteId}`, data)
    return response
  }

  /**
   * 删除笔记
   */
  static async deleteNote(noteId: number): Promise<void> {
    await request.delete(`${API_BASE_URL}/notes/${noteId}`)
  }

  /**
   * 获取所有标签
   */
  static async getTags(): Promise<Tag[]> {
    const response = await request.get(`${API_BASE_URL}/notes/tags`)
    return response
  }

  /**
   * 创建标签
   */
  static async createTag(name: string): Promise<Tag> {
    const response = await request.post(`${API_BASE_URL}/notes/tags`, { name })
    return response
  }

  /**
   * 更新标签
   */
  static async updateTag(tagId: number, name: string): Promise<Tag> {
    const response = await request.patch(`${API_BASE_URL}/notes/tags/${tagId}`, { name })
    return response
  }

  /**
   * 删除标签
   */
  static async deleteTag(tagId: number): Promise<void> {
    await request.delete(`${API_BASE_URL}/notes/tags/${tagId}`)
  }

  /**
   * 合并标签
   */
  static async mergeTags(sourceTagId: number, targetTagId: number): Promise<void> {
    await request.post(`${API_BASE_URL}/notes/tags/merge`, {
      source_tag_id: sourceTagId,
      target_tag_id: targetTagId
    })
  }
} 