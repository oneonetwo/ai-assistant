import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNoteEditorStore = defineStore('noteEditor', () => {
  const draftTitle = ref('')
  const draftContent = ref('')
  const draftMessageIds = ref<number[]>([])

  function setDraft(data: {
    title: string
    content: string
    messageIds: number[]
  }) {
    draftTitle.value = data.title
    draftContent.value = data.content
    draftMessageIds.value = data.messageIds
  }

  function clearDraft() {
    draftTitle.value = ''
    draftContent.value = ''
    draftMessageIds.value = []
  }

  return {
    draftTitle,
    draftContent,
    draftMessageIds,
    setDraft,
    clearDraft
  }
}) 