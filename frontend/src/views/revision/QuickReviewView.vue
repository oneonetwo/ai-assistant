<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast, showLoadingToast, showDialog } from 'vant'
import TaskExecution from '@/components/revision/TaskExecution.vue'
import type { RevisionTask } from '@/types/revision'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()

const planId = Number(route.params.planId)
const tasks = ref<RevisionTask[]>([])
const currentIndex = ref(0)
const pendingUpdates = ref<Array<{
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}>>([])

// 快闪模式相关状态
const isFlashMode = ref(false)
const isPaused = ref(false)
const timer = ref<number | null>(null)
const countdown = ref(10)

const currentTask = computed(() => tasks.value[currentIndex.value] || null)
const progress = computed(() => {
  return tasks.value.length ? 
    Math.round(((currentIndex.value + 1) / tasks.value.length) * 100) : 0
})

// 监听快闪模式状态变化
watch(isFlashMode, (newValue) => {
  if (newValue) {
    startTimer()
  } else {
    stopTimer()
  }
})

// 开始计时器
function startTimer() {
  if (!isPaused.value && isFlashMode.value) {
    countdown.value = 10
    timer.value = window.setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        handleAutoNext()
      }
    }, 1000)
  }
}

// 停止计时器
function stopTimer() {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

// 暂停/继续
function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

// 自动下一个
async function handleAutoNext() {
  stopTimer()
  if (currentIndex.value < tasks.value.length - 1) {
    currentIndex.value++
    startTimer()
  } else {
    await showRestartDialog()
  }
}

async function loadTasks() {
  const loading = showLoadingToast({
    message: '加载中...',
    forbidClick: true,
  })
  
  try {
    // 获取当天的所有任务
    const today = new Date().toISOString().split('T')[0]
    const planTasks = await store.fetchPlanTasks(planId, {
      date: today,
      status: 'pending' // 只获取待复习的任务
    })
    
    if (planTasks.length > 0) {
      tasks.value = planTasks
      currentIndex.value = 0
      if (isFlashMode.value) {
        startTimer()
      }
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

async function showRestartDialog() {
  try {
    await showDialog({
      title: isFlashMode.value ? '快速浏览完成' : '复习完成',
      message: '是否重新浏览所有任务？',
      showCancelButton: true
    })
    // 重置索引并重新开始
    currentIndex.value = 0
    if (isFlashMode.value) {
      startTimer()
    }
  } catch {
    router.back()
  }
}

async function handleTaskComplete(data: {
  taskId: number
  masteryLevel: RevisionTask['mastery_level']
  timeSpent: number
}) {
  if (isFlashMode.value) {
    if (currentIndex.value < tasks.value.length - 1) {
      currentIndex.value++
      startTimer()
    } else {
      await showRestartDialog()
    }
    return
  }

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

      await showRestartDialog()
    } catch (error) {
      showToast('更新状态失败')
    } finally {
      loading.close()
    }
  }
}

// 添加进度显示计算属性
const progressText = computed(() => {
  return `${currentIndex.value + 1}/${tasks.value.length}`
})

onMounted(loadTasks)

// 组件卸载时清理计时器
onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <div class="quick-review">
    <van-nav-bar 
      title="快速复习"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <div class="mode-controls">
          <van-switch
            v-model="isFlashMode"
            size="24"
          />
          <span class="mode-label">闪卡模式</span>
        </div>
      </template>
    </van-nav-bar>
    
    <div class="review-content">
      <div class="progress-bar">
        <van-progress 
          :percentage="progress"
          :show-pivot="true"
        >
          {{ progressText }}
        </van-progress>
      </div>
      
      <div v-if="isFlashMode" class="flash-controls">
        <van-button 
          :type="isPaused ? 'primary' : 'default'"
          size="small"
          @click="togglePause"
        >
          {{ isPaused ? '继续' : '暂停' }}
        </van-button>
        <div class="countdown">{{ countdown }}s</div>
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

<style lang="scss" scoped>
.quick-review {
  height: 100vh;
  display: flex;
  flex-direction: column;

  .mode-controls {
    display: flex;
    align-items: center;
    gap: 8px;

    .mode-label {
      font-size: 14px;
      color: var(--van-text-color);
    }
  }

  .review-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--van-padding-md);
  }

  .progress-bar {
    margin-bottom: var(--van-padding-md);
  }

  .flash-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--van-padding-md);
    padding: var(--van-padding-xs) var(--van-padding-md);
    background: var(--van-background-2);
    border-radius: var(--van-radius-md);

    .countdown {
      font-size: 16px;
      font-weight: 500;
      color: var(--van-primary-color);
    }
  }
}
</style> 