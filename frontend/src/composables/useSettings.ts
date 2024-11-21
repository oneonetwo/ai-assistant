import { ref } from 'vue'

export function useSettings() {
  const settings = ref({
    continuousDialogue: true,
    codeHighlight: true,
    voiceInput: true
  })

  return {
    settings
  }
} 