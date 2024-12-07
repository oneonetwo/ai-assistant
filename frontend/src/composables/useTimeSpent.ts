import { ref } from 'vue'

export function useTimeSpent() {
  const timeSpent = ref(0)
  let startTime: number | null = null
  let intervalId: number | null = null

  function startTimer() {
    if (!startTime) {
      startTime = Date.now()
      intervalId = window.setInterval(() => {
        timeSpent.value = Math.floor((Date.now() - startTime!) / 1000)
      }, 1000)
    }
  }

  function stopTimer() {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
    if (startTime) {
      timeSpent.value = Math.floor((Date.now() - startTime) / 1000)
      startTime = null
    }
  }

  return {
    timeSpent,
    startTimer,
    stopTimer
  }
} 