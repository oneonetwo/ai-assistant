<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import TaskReviewCard from '@/components/revision/TaskReviewCard.vue'
import type { RevisionTask } from '@/types/revision'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()

// 获取计划ID  有就传，没有就null
const planId = Number(route.params.id)

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
  try {
    // 一次性获取所有待复习任务
    const task = await store.getNextTask({ planId, mode: 'quick' })
    if (task) {
      tasks.value = [task]
      // 继续获取更多任务
    //   while (true) {
    //     const nextTask = await store.getNextTask({ planId, mode: 'quick' })
    //     if (!nextTask) break
    //     tasks.value.push(nextTask)
    //   }
    }
  } catch (error) {
    showToast('加载任务失败')
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
    // 批量提交所有更新
    try {
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
      
      <TaskReviewCard
        v-if="currentTask"
        :task="currentTask"
        mode="quick"
      />
    </div>
  </div>
</template> 