<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast, showLoadingToast } from 'vant'
import TaskExecution from '@/components/revision/TaskExecution.vue'
import type { RevisionTask } from '@/types/revision'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()

const tasks = ref<RevisionTask[]>([])
const currentIndex = ref(0)
const pendingUpdates = ref<Array<{
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}>>([])

const currentTask = computed(() => tasks.value[currentIndex.value] || null)
const progress = computed(() => {
  return tasks.value.length ? 
    Math.round(((currentIndex.value + 1) / tasks.value.length) * 100) : 0
})

async function loadTasks() {
  const loading = showLoadingToast({
    message: '加载中...',
    forbidClick: true,
  })
  try {
    const task = await store.getNextTask({ 
      plan_id: Number(route.params.id), 
      mode: 'quick' 
    })
    if (task) {
      tasks.value = [task]
      // 继续获取更多任务
      const nextTask = await store.getNextTask({ 
        plan_id: Number(route.params.id), 
        mode: 'quick' 
      })
      if (nextTask) {
        tasks.value.push(nextTask)
      }
    } else {
      showToast('没有需要复习的任务')
      router.back()
    }
  } catch (error) {
    showToast('加载任务失败')
  } finally {
    loading.close()
  }
}

async function handleTaskComplete(data: {
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}) {
  pendingUpdates.value.push(data)
  
  if (currentIndex.value < tasks.value.length - 1) {
    currentIndex.value++
  } else {
    const loading = showLoadingToast({
      message: '更新中...',
      forbidClick: true,
    })
    try {
      // 批量提交所有更新
      await store.batchUpdateTasks({
        task_ids: pendingUpdates.value.map(u => u.taskId),
        status: 'completed',
        mastery_level: pendingUpdates.value[pendingUpdates.value.length - 1].masteryLevel,
        revision_mode: 'quick',
        time_spent: pendingUpdates.value.reduce((sum, u) => sum + u.timeSpent, 0)
      })

      // 处理未掌握的任务
      for (const update of pendingUpdates.value) {
        if (update.masteryLevel !== 'mastered') {
          const nextDate = new Date()
          nextDate.setDate(nextDate.getDate() + 1)
          
          await store.adjustTaskSchedule({
            task_id: update.taskId,
            new_date: nextDate.toISOString(),
            priority: update.masteryLevel === 'not_mastered' ? 1 : 2
          })
        }
      }

      showToast('复习完成')
      router.back()
    } catch (error) {
      showToast('更新状态失败')
    } finally {
      loading.close()
    }
  }
}

onMounted(loadTasks)
</script>

<template>
  <div class="quick-review">
    <van-nav-bar 
      title="快速复习"
      left-arrow
      @click-left="router.back()"
    />
    
    <div class="review-content">
      <div class="progress-bar">
        <van-progress 
          :percentage="progress"
          :show-pivot="true"
        >
          {{ currentIndex + 1 }}/{{ tasks.length }}
        </van-progress>
      </div>
      
      <TaskExecution
        v-if="currentTask"
        :task="currentTask"
        mode="quick"
        @complete="handleTaskComplete"
      />
    </div>
  </div>
</template> 