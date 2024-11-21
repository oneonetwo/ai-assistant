<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { usePermission } from '@vueuse/core'
import { showToast } from 'vant'

const emit = defineEmits<{
  (e: 'text', value: string): void
}>()

const isListening = ref(false)
const transcript = ref('')
const micPermission = usePermission('microphone')
let recognition: SpeechRecognition | null = null

// 检查浏览器支持
const isSupported = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window

// 初始化语音识别
function initRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SpeechRecognition()
  
  recognition.lang = 'zh-CN'
  recognition.continuous = true
  recognition.interimResults = true
  
  recognition.onresult = (event) => {
    let finalTranscript = ''
    let interimTranscript = ''
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i]
      if (result.isFinal) {
        finalTranscript += result[0].transcript
      } else {
        interimTranscript += result[0].transcript
      }
    }
    
    transcript.value = finalTranscript || interimTranscript
  }
  
  recognition.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    showToast('语音识别出错，请重试')
    stopListening()
  }
  
  recognition.onend = () => {
    if (isListening.value) {
      recognition?.start()
    }
  }
}

async function startListening() {
  if (!isSupported) {
    showToast('您的浏览器不支持语音识别')
    return
  }
  
  if (micPermission.value !== 'granted') {
    showToast('请允许使用麦克风')
    return
  }
  
  try {
    if (!recognition) {
      initRecognition()
    }
    
    isListening.value = true
    transcript.value = ''
    recognition?.start()
  } catch (error) {
    console.error('启动语音识别失败:', error)
    showToast('启动语音识别失败')
  }
}

function stopListening() {
  isListening.value = false
  recognition?.stop()
  
  if (transcript.value) {
    emit('text', transcript.value)
    transcript.value = ''
  }
}

onUnmounted(() => {
  recognition?.stop()
})
</script>

<template>
  <div class="voice-input">
    <van-button
      :type="isListening ? 'danger' : 'primary'"
      size="small"
      :icon="isListening ? 'stop-circle-o' : 'microphone-o'"
      @touchstart="startListening"
      @touchend="stopListening"
      @mousedown="startListening"
      @mouseup="stopListening"
    >
      {{ isListening ? '正在录音...' : '按住说话' }}
    </van-button>
    
    <transition name="fade">
      <div v-if="transcript" class="transcript">
        {{ transcript }}
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.voice-input {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--van-padding-xs);
}

.transcript {
  font-size: 14px;
  color: var(--van-text-color-2);
  text-align: center;
  max-width: 300px;
  
  &.fade-enter-active,
  &.fade-leave-active {
    transition: opacity 0.3s ease;
  }
  
  &.fade-enter-from,
  &.fade-leave-to {
    opacity: 0;
  }
}
</style> 