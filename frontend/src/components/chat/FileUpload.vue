<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'

const props = defineProps<{
  accept?: string
  maxSize?: number // 单位：MB
}>()

const emit = defineEmits<{
  (e: 'upload', file: File): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

// 文件类型验证
const validateFile = (file: File) => {
  // 验证文件类型
  const supportedTypes = {
    image: ['image/jpeg', 'image/png', 'image/gif'],
    document: [
      'text/plain',
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/epub+zip',
      'text/markdown'
    ]
  }

  const isValidType = [...supportedTypes.image, ...supportedTypes.document].includes(file.type)
  if (!isValidType) {
    showToast('不支持的文件类型')
    return false
  }

  // 验证文件大小
  const maxSize = (props.maxSize || 10) * 1024 * 1024 // 默认10MB
  if (file.size > maxSize) {
    showToast(`文件大小不能超过${props.maxSize}MB`)
    return false
  }

  return true
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (file && validateFile(file)) {
    emit('upload', file)
  }
  
  // 重置input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 处理拖拽
const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false
  
  const file = event.dataTransfer?.files[0]
  if (file && validateFile(file)) {
    emit('upload', file)
  }
}
</script>

<template>
  <div 
    class="file-upload"
    :class="{ dragging: isDragging }"
    @dragenter.prevent="isDragging = true"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop="handleDrop"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      class="file-input"
      @change="handleFileSelect"
    >
    <div class="upload-content">
      <svg-icon name="upload" />
      <p>点击或拖拽文件到此处上传</p>
      <p class="tip">支持图片和文档文件</p>
    </div>
  </div>
</template>
