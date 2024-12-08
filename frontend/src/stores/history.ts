import { defineStore } from 'pinia'
import { ref } from 'vue'
import { HistoryAPI } from '@/services/historyService'
import type { RevisionHistory, NoteStatistics } from '@/types/history'

export const useHistoryStore = defineStore('history', () => {
  const noteHistory = ref<RevisionHistory[]>([])
  const noteStatistics = ref<NoteStatistics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchNoteHistory(noteId: number) {
    isLoading.value = true
    error.value = null
    try {
      noteHistory.value = await HistoryAPI.getNoteHistory(noteId)
    } catch (err) {
      error.value = '获取历史记录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchNoteStatistics(noteId: number) {
    isLoading.value = true
    error.value = null
    try {
      noteStatistics.value = await HistoryAPI.getNoteStatistics(noteId)
    } catch (err) {
      error.value = '获取统计数据失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    noteHistory,
    noteStatistics,
    isLoading,
    error,
    fetchNoteHistory,
    fetchNoteStatistics
  }
}) 