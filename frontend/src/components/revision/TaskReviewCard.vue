<script setup lang="ts">
import { ref } from 'vue'
import type { RevisionTask } from '@/types/revision'

const props = defineProps<{
  task: RevisionTask
  mode: 'normal' | 'quick'
}>()

const emit = defineEmits<{
  (e: 'complete', data: {
    taskId: number
    masteryLevel: RevisionTask['mastery_level']
    timeSpent?: number
  }): void
}>()

const showContent = ref(props.mode === 'normal')
const startTime = ref(Date.now())

function handleComplete(masteryLevel: RevisionTask['mastery_level']) {
  const timeSpent = Date.now() - startTime.value
  emit('complete', {
    taskId: props.task.id,
    masteryLevel,
    timeSpent: Math.round(timeSpent / 1000)
  })
}
</script>

<template>
  <div class="task-review-card">
    <div class="card-header">
      <h3>{{ task.note.title }}</h3>
      <van-tag :type="task.note.priority">{{ task.note.priority }}</van-tag>
    </div>

    <div 
      v-if="mode === 'quick'"
      class="quick-review-toggle"
      @click="showContent = !showContent"
    >
      <van-button block>{{ showContent ? '隐藏内容' : '显示内容' }}</van-button>
    </div>

    <div v-show="showContent" class="card-content">
      <div class="markdown-body" v-html="task.note.content" />
    </div>

    <div class="card-actions">
      <van-button 
        type="danger" 
        @click="handleComplete('not_mastered')"
      >
        未掌握
      </van-button>
      <van-button 
        type="warning"
        @click="handleComplete('partially_mastered')"
      >
        部分掌握
      </van-button>
      <van-button 
        type="success"
        @click="handleComplete('mastered')"
      >
        已掌握
      </van-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.task-review-card {
  padding: 16px;
  background: var(--van-background-2);
  border-radius: 8px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .quick-review-toggle {
    margin-bottom: 16px;
  }

  .card-content {
    margin-bottom: 16px;
    padding: 16px;
    background: var(--van-background);
    border-radius: 4px;
  }

  .card-actions {
    display: flex;
    gap: 8px;

    .van-button {
      flex: 1;
    }
  }
}
</style> 