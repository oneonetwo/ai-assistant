import { defineStore } from 'pinia'
import { ref } from 'vue'
import { HistoryAPI } from '@/services/historyService'
import type { RevisionHistory, NoteStatistics } from '@/types/history'

// 生成过去30天的模拟数据
function generateMockTrends() {
  const trends = [];
  const now = new Date();
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    trends.push({
      date: date.toISOString().split('T')[0],
      count: Math.floor(Math.random() * 5), // 0-4次
      duration: Math.floor(Math.random() * 30 + 10), // 10-40分钟
      quality: Math.floor(Math.random() * 30 + 70) // 70-100分
    });
  }
  
  return trends;
}

export const useHistoryStore = defineStore('history', {
  state: () => ({
    noteHistory: [] as RevisionHistory[],
    noteStatistics: null as NoteStatistics | null,
  }),
  
  actions: {
    async fetchNoteHistory(noteId: number) {
      this.isLoading = true
      this.error = null
      try {
        this.noteHistory = await HistoryAPI.getNoteHistory(noteId)
      } catch (err) {
        this.error = '获取历史记录失败'
        throw err
      } finally {
        this.isLoading = false
      }
    },
    async fetchNoteStatistics(noteId: number) {
      // 模拟API调用
      this.noteStatistics = {
        total_revisions: 45,
        mastery_levels: {
          low: 5,
          medium: 15,
          high: 25
        },
        revision_trends: generateMockTrends(),
        average_duration: 25,
        average_quality: 85
      };
    },
  }
}) 