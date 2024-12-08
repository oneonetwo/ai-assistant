<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import TaskSummaryCard from '@/components/revision/TaskSummaryCard.vue'
import dayjs from 'dayjs'
import TaskExecution from '@/components/revision/TaskExecution.vue'

const store = useNotificationStore()
const router = useRouter()
const showTaskExecution = ref(false)
const currentTask = ref<RevisionTask | null>(null)

// 计算今日日期
const today = computed(() => {
  return store.summary?.date ? dayjs(store.summary.date).format('YYYY年MM月DD日') : ''
})

// 按优先级分组的任务
const groupedTasks = computed(() => {
  if (!store.summary?.tasks) return []
  
  return store.summary.tasks.reduce((acc, task) => {
    const priority = task.priority
    if (!acc[priority]) acc[priority] = []
    acc[priority].push(task)
    return acc
  }, {} as Record<number, typeof store.summary.tasks>)
})

// 格式化时间
function formatTime(dateStr: string) {
  return dayjs(dateStr).format('HH:mm')
}

// 计算任务统��数据
const taskStats = computed(() => {
  if (!store.summary?.tasks) return { pending: 0, upcoming: 0, completed: 0 }
  
  return store.summary.tasks.reduce((acc, task) => {
    if (task.status === 'completed') {
      acc.completed++
    } else {
      // 判断是否即将到期（24小时内）
      const scheduledTime = dayjs(task.scheduled_date)
      const isUpcoming = scheduledTime.diff(dayjs(), 'hour') <= 24
      
      if (isUpcoming) {
        acc.upcoming++
      } else {
        acc.pending++
      }
    }
    return acc
  }, { pending: 0, upcoming: 0, completed: 0 })
})

onMounted(async () => {
  try {
    await store.fetchSummary()
  } catch (error) {
    showToast('获取摘要失败')
  }
})

// 处理任务点击
function handleTaskClick(task: RevisionTask) {
  currentTask.value = task
  showTaskExecution.value = true
}

// 处理任务状态更新
async function handleTaskStatusChange(taskId: number, masteryLevel: RevisionTask['mastery_level']) {
  try {
    await store.updateTaskStatus(taskId, masteryLevel)
    // 更新本地任务状态
    if (store.summary?.tasks) {
      const taskIndex = store.summary.tasks.findIndex(t => t.task_id === taskId)
      if (taskIndex !== -1) {
        store.summary.tasks[taskIndex].status = masteryLevel === 'mastered' ? 'completed' : 'pending'
      }
    }
  } catch (error) {
    showToast('更新任务状态失败')
  }
}

// 开始复习当天任务
function startDailyRevision() {
  router.push({ 
    name: 'revision-task-review',
    query: { date: store.summary?.date }
  })
}

// 快速复习模式
function startQuickRevision() {
  router.push({ 
    name: 'revision-quick-review',
    query: { date: store.summary?.date }
  })
}
</script>

<template>
  <div class="daily-summary">
    <van-nav-bar
      title="每日摘要"
      left-arrow
      @click-left="$router.back()"
    />
    
    <div class="summary-content">
      <!-- 日期和消息提示 -->
      <div class="summary-header">
        <h2>{{ today }}</h2>
        <p class="message">{{ store.summary?.message }}</p>
      </div>

      <!-- 统计卡片 -->
      <div class="summary-cards">
        <TaskSummaryCard
          v-if="store.summary"
          title="待复习"
          :count="taskStats.pending"
          type="pending"
        />
        
        <TaskSummaryCard
          v-if="store.summary"
          title="即将到期"
          :count="taskStats.upcoming"
          type="upcoming"
        />
        
        <TaskSummaryCard
          v-if="store.summary"
          title="已完成"
          :count="taskStats.completed"
          type="completed"
        />
      </div>
      
      <!-- 任务列表 -->
      <div v-if="store.summary?.tasks.length" class="task-list">
        <template v-for="(tasks, priority) in groupedTasks" :key="priority">
          <div class="priority-group">
            <div class="priority-label">
              <van-tag :type="['success', 'warning', 'danger'][priority]">
                {{ ['普通', '重要', '紧急'][priority] }}
              </van-tag>
            </div>
            
            <van-cell-group inset>
              <van-cell
                v-for="task in tasks"
                :key="task.task_id"
                :title="task.note.title"
                :label="formatTime(task.scheduled_date)"
                is-link
                :class="{ 'completed': task.status === 'completed' }"
                @click="handleTaskClick(task)"
              >
                <template #right-icon>
                  <van-tag 
                    :type="task.status === 'completed' ? 'success' : 'default'"
                    round
                  >
                    {{ task.status === 'completed' ? '已完成' : '待复习' }}
                  </van-tag>
                </template>
              </van-cell>
            </van-cell-group>
          </div>
        </template>
      </div>
      
      <!-- Task Execution Popup -->
      <van-popup
        v-model:show="showTaskExecution"
        :style="{ width: '90%', height: '70%' }"
        round
      >
        <TaskExecution
          v-if="currentTask"
          :task="currentTask"
          @status-change="handleTaskStatusChange"
        />
      </van-popup>
      
      <!-- 底部按钮 -->
      <div class="review-actions">
        <van-button 
          type="primary" 
          block 
          @click="startDailyRevision"
        >
          开始逐条复习
        </van-button>
        
        <van-button 
          type="success" 
          block 
          @click="startQuickRevision"
        >
          快速复习模式
        </van-button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.daily-summary {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .summary-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    
    .summary-header {
      margin-bottom: 20px;
      text-align: center;
      
      h2 {
        margin: 0;
        font-size: 20px;
        color: var(--van-text-color);
      }
      
      .message {
        margin: 8px 0 0;
        font-size: 14px;
        color: var(--van-text-color-2);
      }
    }
    
    .summary-cards {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 24px;
    }
    
    .task-list {
      margin-bottom: 80px; // 为底部按钮留出空间
      
      .priority-group {
        margin-bottom: 20px;
        
        .priority-label {
          margin-bottom: 8px;
          padding: 0 16px;
        }
      }
      
      .completed {
        opacity: 0.6;
        
        :deep(.van-cell__title) {
          text-decoration: line-through;
        }
      }
    }
  }
}

.review-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);
  
  display: flex;
  gap: 16px;
  z-index: 99;
}
</style> 