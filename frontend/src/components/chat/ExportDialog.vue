<script setup lang="ts">
import { ref } from 'vue'
import { exportMessages } from '@/utils/export'
import { exportToPDF } from '@/utils/pdf-export'

const props = defineProps<{
  messages: Message[]
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>()

const exportFormat = ref<'markdown' | 'json' | 'txt' | 'pdf'>('markdown')

async function handleExport() {
  if (exportFormat.value === 'pdf') {
    await exportToPDF(props.messages, {
      title: '聊天记录导出',
      author: '用户'
    })
  } else {
    exportMessages(props.messages, {
      format: exportFormat.value
    })
  }
  emit('update:show', false)
}
</script>

<template>
  <van-dialog
    v-model:show="show"
    title="导出对话"
    show-cancel-button
    @confirm="handleExport"
  >
    <div class="export-options">
      <van-radio-group v-model="exportFormat">
        <van-cell-group inset>
          <van-cell title="Markdown 格式">
            <template #right-icon>
              <van-radio name="markdown" />
            </template>
          </van-cell>
          <van-cell title="PDF 格式">
            <template #right-icon>
              <van-radio name="pdf" />
            </template>
          </van-cell>
          <van-cell title="JSON 格式">
            <template #right-icon>
              <van-radio name="json" />
            </template>
          </van-cell>
          <van-cell title="纯文本格式">
            <template #right-icon>
              <van-radio name="txt" />
            </template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>
    </div>
  </van-dialog>
</template>

<style lang="scss" scoped>
.export-options {
  padding: 16px;
}
</style> 