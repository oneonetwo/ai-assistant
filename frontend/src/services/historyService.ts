import { request } from '@/utils/request'
import type { RevisionHistory, NoteStatistics } from '@/types/history'

const API_BASE = '/api/v1/revision-settings'

export class HistoryAPI {
  static async getNoteHistory(noteId: number): Promise<RevisionHistory[]> {
    const response = await request.get(`${API_BASE}/history/note/${noteId}`)
    return response
  }

  static async getNoteStatistics(noteId: number): Promise<NoteStatistics> {
    const response = await request.get(`${API_BASE}/statistics/note/${noteId}`)
    return response
  }
} 