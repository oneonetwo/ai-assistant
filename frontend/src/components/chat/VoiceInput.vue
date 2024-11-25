<script setup lang="ts">
import { ref } from 'vue'

const isListening = ref(false)
const transcript = ref('')

// 开始录音
function startListening() {
  isListening.value = true
  // TODO: 实现语音识别逻辑
}

// 停止录音
function stopListening() {
  isListening.value = false
  // TODO: 停止语音识别并发送结果
  emit('input', transcript.value)
}

const emit = defineEmits(['input'])
</script>

<template>
  <van-button
    :type="isListening ? 'danger' : 'default'"
    size="small"
    :icon="isListening ? 'stop-circle-o' : 'microphone-o'"
    @touchstart="startListening"
    @touchend="stopListening"
    @mousedown="startListening"
    @mouseup="stopListening"
  >
    {{ isListening ? '正在录音...' : '按住说话' }}
  </van-button>
</template>

<style lang="scss" scoped>
.van-button {
  height: 36px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  
  &--danger {
    background: var(--van-error-color);
    border-color: var(--van-error-color);
  }
}
</style> 