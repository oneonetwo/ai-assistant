<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import TaskReviewCard from '@/components/revision/TaskReviewCard.vue'
import type { RevisionTask } from '@/types/revision'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()

const currentTask = ref<RevisionTask | null>(null)
const planId = Number(route.params.planId)

async function loadNextTask() {
  try {
    const task = await store.getNextTask({ 
      plan_id: planId,
      mode: 'normal'
    })
    currentTask.value = task
  } catch (error) {
    showToast('加载任务失败')
  }
}

async function handleTaskComplete(data: {
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}) {
  try {
    await store.batchUpdateTasks({
      task_ids: [data.taskId],
      status: 'completed',
      mastery_level: data.masteryLevel,
      revision_mode: 'normal',
      time_spent: data.timeSpent
    })
    
    // 如果是未掌握或部分掌握，自动调整计划
    if (data.masteryLevel !== 'mastered') {
      const nextDate = new Date()
      nextDate.setDate(nextDate.getDate() + 1) // 第二天复习
      
      await store.adjustTaskSchedule({
        task_id: data.taskId,
        new_date: nextDate.toISOString(),
        priority: data.masteryLevel === 'not_mastered' ? 1 : 2
      })
    }
    
    await loadNextTask()
  } catch (error) {
    showToast('更新任务状态失败')
  }
}

onMounted(loadNextTask)
</script>

<template>
  <div class="task-review">
    <van-nav-bar 
      title="逐条复习"
      left-arrow
      @click-left="router.back()"
    />
    
    <div class="review-content">
      <TaskReviewCard
        v-if="currentTask"
        :task="currentTask"
        mode="normal"
        @complete="handleTaskComplete"
      />
      
      <van-empty 
        v-else
        description="已完成所有任务"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.task-review {
  height: 100%;
  display: flex;
  flex-direction: column;

  .review-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}
</style> 