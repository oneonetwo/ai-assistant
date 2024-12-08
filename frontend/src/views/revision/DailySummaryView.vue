<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import TaskSummaryCard from '@/components/revision/TaskSummaryCard.vue'
import dayjs from 'dayjs'

const store = useNotificationStore()
const router = useRouter()

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

// 计算任务统计数据
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

function startRevision() {
  router.push({ name: 'revision-tasks' })
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
                :title="task.note_title"
                :label="formatTime(task.scheduled_date)"
                is-link
                :class="{ 'completed': task.status === 'completed' }"
                @click="router.push(`/revision/tasks/${task.task_id}`)"
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
      
      <!-- 底部按钮 -->
      <div class="summary-actions">
        <van-button 
          block 
          type="primary"
          size="large"
          @click="startRevision"
        >
          开始复习
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
    
    .summary-actions {
      margin-top: 24px;
      padding: 16px 0;
    }
  }
}
</style> 