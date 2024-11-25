<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  error?: string
  quote?: {
    code: string
    language: string
  }
}

const props = defineProps<{
  message: Message
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'save', content: string): void
}>()

const editContent = ref(props.message.content)

function handleSave() {
  const content = editContent.value.trim()
  if (!content) {
    showToast('消息内容不能为空')
    return
  }
  
  emit('save', content)
  emit('update:show', false)
}
</script>

<template>
  <van-popup
    :show="show"
    position="bottom"
    :style="{ height: '50%' }"
    round
    closeable
    @update:show="$emit('update:show', $event)"
  >
    <div class="message-editor">
      <div class="editor-header">
        <span class="title">编辑消息</span>
      </div>
      
      <div class="editor-content">
        <van-field
          v-model="editContent"
          type="textarea"
          rows="10"
          autosize
          placeholder="请输入消息内容"
        />
      </div>
      
      <div class="editor-footer">
        <van-button 
          block 
          type="primary"
          :loading="loading"
          @click="handleSave"
        >
          保存
        </van-button>
      </div>
    </div>
  </van-popup>
</template>

<style lang="scss" scoped>
.message-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  
  .editor-header {
    text-align: center;
    margin-bottom: 16px;
    
    .title {
      font-size: 16px;
      font-weight: 500;
    }
  }
  
  .editor-content {
    flex: 1;
    overflow-y: auto;
    
    :deep(.van-field__control) {
      height: 100%;
      resize: none;
    }
  }
  
  .editor-footer {
    margin-top: 16px;
  }
}
</style> 