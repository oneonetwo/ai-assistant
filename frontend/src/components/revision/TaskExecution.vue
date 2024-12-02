<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RevisionTask } from '@/types/revision'

const props = defineProps<{
  task: RevisionTask
}>()

const emit = defineEmits<{
  (e: 'status-change', status: RevisionTask['status']): void
}>()

const showContent = ref(false)

const statusOptions = [
  { text: '未掌握', value: 'not_mastered' },
  { text: '部分掌握', value: 'partially_mastered' },
  { text: '已掌握', value: 'mastered' }
]

const statusColor = computed(() => {
  switch (props.task.status) {
    case 'mastered':
      return 'success'
    case 'partially_mastered':
      return 'warning'
    default:
      return 'danger'
  }
})
</script>

<template>
  <div class="task-execution">
    <div class="task-header">
      <h3>{{ task.title }}</h3>
      <van-tag :type="statusColor">
        {{ statusOptions.find(opt => opt.value === task.status)?.text }}
      </van-tag>
    </div>

    <div class="task-actions">
      <van-button
        block
        @click="showContent = !showContent"
      >
        {{ showContent ? '隐藏内容' : '显示内容' }}
      </van-button>
    </div>

    <div v-show="showContent" class="task-content">
      <div class="markdown-body" v-html="task.content" />
    </div>

    <div class="status-buttons">
      <van-button-group>
        <van-button
          v-for="option in statusOptions"
          :key="option.value"
          :type="task.status === option.value ? statusColor : 'default'"
          @click="emit('status-change', option.value)"
        >
          {{ option.text }}
        </van-button>
      </van-button-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.task-execution {
  padding: 16px;

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      font-size: 16px;
      font-weight: 500;
    }
  }

  .task-actions {
    margin-bottom: 16px;
  }

  .task-content {
    margin-bottom: 16px;
    padding: 16px;
    background: var(--van-background-2);
    border-radius: 8px;
  }

  .status-buttons {
    .van-button-group {
      display: flex;
      gap: 8px;
    }
  }
}
</style> 