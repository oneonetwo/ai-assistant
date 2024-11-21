<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'

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
    @update:show="$emit('update:show', $event)"
    position="bottom"
    :style="{ height: '50%' }"
  >
    <div class="message-editor">
      <div class="editor-header">
        <span>编辑消息</span>
        <van-button 
          plain 
          size="small"
          @click="$emit('update:show', false)"
        >
          取消
        </van-button>
      </div>
      
      <div class="editor-content">
        <van-field
          v-model="editContent"
          type="textarea"
          rows="6"
          autosize
          maxlength="2000"
          show-word-limit
        />
      </div>
      
      <div class="editor-footer">
        <van-button
          block
          type="primary"
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
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--van-padding-sm);
  border-bottom: 1px solid var(--van-border-color);
}

.editor-content {
  flex: 1;
  padding: var(--van-padding-sm);
  overflow-y: auto;
}

.editor-footer {
  padding: var(--van-padding-sm);
  border-top: 1px solid var(--van-border-color);
}
</style> 