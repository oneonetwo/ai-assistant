<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast, showLoadingToast, showDialog } from 'vant'
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

const planId = Number(route.query.planId)
const date = route.query.date as string

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
    let planTasks: RevisionTask[]
    if (planId) {
      // 获取计划的待复习任务  日期不设限
      planTasks = await store.fetchPlanTasks(planId, {
        status: 'pending'
      })
    } else if (date) {
      // 获取指定日期的待复习任务 date获取当天不需要传递
      const response = await store.fetchDailyTasks({
        status: 'pending'
      })
      planTasks = response.filter(task => task.status === 'pending')
    } else {
      throw new Error('缺少必要参数')
    }
    
    if (planTasks.length > 0) {
      tasks.value = planTasks
      currentIndex.value = 0
    } else {
      // 如果没有任务，显示提示并返回
      await showDialog({
        title: '提示',
        message: '当前没有待复习的任务',
        showCancelButton: false,
        confirmButtonText: '返回'
      })
      router.back()
    }
  } catch (error) {
    showToast('加载任务失败')
    console.error('加载任务失败:', error)
  } finally {
    loading.close()
  }
}

async function handleTaskComplete(data: {
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}) {
  const loading = showLoadingToast({
    message: '更新中...',
    forbidClick: true,
  })
  
  try {
    // 单个更新任务状态
    await store.batchUpdateTasks({
      task_ids: [data.taskId],
      status: 'completed',
      mastery_level: data.masteryLevel,
      revision_mode: 'normal',
      time_spent: data.timeSpent
    })
    
    // 如果未掌握，立即调整计划
    if (data.masteryLevel !== 'mastered') {
      const nextDate = new Date()
      nextDate.setDate(nextDate.getDate() + 1)
      
      await store.adjustTaskSchedule({
        task_id: data.taskId,
        new_date: nextDate.toISOString(),
        priority: data.masteryLevel === 'not_mastered' ? 1 : 2
      })
    }
    
    // 继续下一个任务或完成复习
    if (currentIndex.value < tasks.value.length - 1) {
      currentIndex.value++
    } else {
      await showDialog({
        title: '复习完成',
        message: '已完成所有任务',
        showCancelButton: false,
        confirmButtonText: '返回'
      })
      router.back()
    }
  } catch (error) {
    showToast('更新任务状态失败')
    console.error('更新任务状态失败:', error)
  } finally {
    loading.close()
  }
}

onMounted(loadTasks)
</script>

<template>
  <div class="task-review">
    <van-nav-bar 
      title="逐条复习"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <span class="progress-text">{{ progress }}%</span>
      </template>
    </van-nav-bar>
    
    <div class="review-content">
      <TaskExecution
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

  .progress-text {
    font-size: 14px;
    color: var(--van-text-color);
  }

  .review-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}
</style> 