import { ref } from 'vue'

export function useVoiceRecognition() {
  const isRecording = ref(false)
  const recognition = ref<SpeechRecognition | null>(null)

  // 检查浏览器是否支持语音识别
  const isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window

  // 初始化语音识别
  function initRecognition() {
    if (!isSupported) return

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition.value = new SpeechRecognition()
    
    if (recognition.value) {
      recognition.value.continuous = false
      recognition.value.interimResults = false
      recognition.value.lang = 'zh-CN' // 设置语言
    }
  }

  // 开始录音
  function startRecording(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!recognition.value) {
        initRecognition()
      }

      if (!recognition.value) {
        reject(new Error('语音识别不可用'))
        return
      }

      isRecording.value = true

      recognition.value.onresult = (event) => {
        const result = event.results[0][0].transcript
        resolve(result)
        stopRecording()
      }

      recognition.value.onerror = (event) => {
        reject(new Error('语音识别失败'))
        stopRecording()
      }

      recognition.value.start()
    })
  }

  // 停止录音
  function stopRecording() {
    if (recognition.value) {
      recognition.value.stop()
    }
    isRecording.value = false
  }

  return {
    isRecording,
    isSupported,
    startRecording,
    stopRecording
  }
} 