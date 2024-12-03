<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '@/utils/date'

interface Note {
  id: number
  title: string
  content: string
  status: string
  priority: 'low' | 'medium' | 'high'
}

interface RevisionTask {
  id: number
  plan_id: number
  note_id: number
  scheduled_date: string
  status: 'pending' | 'completed'
  mastery_level: number | null
  revision_count: number
  created_at: string
  completed_at: string | null
  note: Note
}

const props = defineProps<{
  tasks: RevisionTask[]
}>()

const emit = defineEmits<{
  (e: 'complete', taskId: number): void
}>()

const sortedTasks = computed(() => {
  return [...props.tasks].sort((a, b) => 
    new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime()
  )
})

function handleComplete(taskId: number) {
  emit('complete', taskId)
}

function getPriorityColor(priority: string) {
  const colors = {
    low: 'var(--van-blue)',
    medium: 'var(--van-orange)',
    high: 'var(--van-red)'
  }
  return colors[priority] || colors.low
}
</script>

<template>
  <div class="revision-list">
    <van-empty v-if="!tasks.length" description="暂无复习任务" />
    
    <div v-else class="task-list">
      <van-cell-group
        v-for="task in sortedTasks"
        :key="task.id"
        :title="formatDate(task.scheduled_date)"
        class="task-group"
      >
        <van-cell>
          <template #title>
            <div class="task-header">
              <span class="task-title">{{ task.note.title }}</span>
              <van-tag 
                :color="getPriorityColor(task.note.priority)"
                size="small"
              >
                {{ task.note.priority }}
              </van-tag>
            </div>
          </template>
          
          <template #label>
            <div class="task-content">
              <p class="preview-text">{{ task.note.content.slice(0, 50) }}...</p>
              <div class="task-meta">
                <span>复习次数: {{ task.revision_count }}</span>
                <span>状态: {{ task.note.status }}</span>
              </div>
            </div>
          </template>
          
          <template #right-icon>
            <van-button 
              size="small"
              type="primary"
              :disabled="task.status === 'completed'"
              @click="handleComplete(task.id)"
            >
              {{ task.status === 'completed' ? '已完成' : '完成' }}
            </van-button>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.revision-list {
  padding: var(--van-padding-sm);
}

.task-group {
  margin-bottom: var(--van-padding-sm);
  background: var(--van-background-2);
  border-radius: var(--van-radius-md);
  overflow: hidden;
}

.task-header {
  display: flex;
  align-items: center;
  gap: var(--van-padding-xs);
  
  .task-title {
    font-weight: 500;
    font-size: 16px;
  }
}

.task-content {
  .preview-text {
    margin: var(--van-padding-xs) 0;
    color: var(--van-text-color-2);
    font-size: 14px;
  }
  
  .task-meta {
    display: flex;
    gap: var(--van-padding-md);
    font-size: 12px;
    color: var(--van-gray-6);
  }
}
</style> 