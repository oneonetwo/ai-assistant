<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionTask } from '@/types/revision'
import { formatDate } from '@/utils/date'
import TaskExecution from '@/components/revision/TaskExecution.vue'
import { formatISODate } from '@/utils/dateFormat' // 导入时间处理函数


const route = useRoute()
const router = useRouter()
const store = useRevisionStore()
const showTaskExecution = ref(false)
const currentTask = ref<RevisionTask | null>(null)

// 筛选条件
const filterDate = ref('')
const filterStatus = ref<'pending' | 'completed' | 'skipped' | ''>('')

// 使用 formatISODate 格式化时间
const formattedStartDate = computed(() => formatISODate(planDetails.value.start_date))
const formattedEndDate = computed(() => formatISODate(planDetails.value.end_date))


const planId = Number(route.params.id)
const planDetails = ref({
  name: '',
  start_date: '',
  end_date: '',
  status: ''
})

onMounted(async () => {
  await fetchPlanDetails()
  await fetchPlanTasks()
})

async function fetchPlanDetails() {
  try {
    const plan = await store.fetchPlan(planId)
    planDetails.value = {
      name: plan.name,
      start_date: formatDate(new Date(plan.start_date).getTime()),
      end_date: formatDate(new Date(plan.end_date).getTime()),
      status: plan.status
    }
  } catch (error) {
    showToast('获取计划详情失败')
  }
}

async function fetchPlanTasks() {
  try {
    const params = {
      ...(filterDate.value && { date: filterDate.value }),
      ...(filterStatus.value && { status: filterStatus.value })
    }
    await store.fetchPlanTasks(planId, params)
  } catch (error) {
    showToast('获取计划任务失败')
  }
}

// 筛选变化时重新获取数据
async function handleFilterChange() {
  await fetchPlanTasks()
}

const groupedTasks = computed(() => {
  const groups: Record<string, RevisionTask[]> = {}
  store.planTasks.forEach(task => {
    const date = task.scheduled_date ? 
      formatDate(new Date(task.scheduled_date).getTime()) : 
      'Unknown Date'
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(task)
  })
  return Object.entries(groups).map(([date, tasks]) => ({
    date,
    tasks
  }))
})

const progress = computed(() => {
  const total = store.planTasks.length
  if (total === 0) return 0
  const completed = store.planTasks.filter(task => 
    task.mastery_level === 'mastered' || task.mastery_level === 'partially_mastered'
  ).length
  return Math.round((completed / total) * 100)
})

function handleTaskClick(task: RevisionTask) {
  currentTask.value = task
  showTaskExecution.value = true
}

async function handleTaskStatusChange(taskId: number, masteryLevel  : RevisionTask['mastery_level']) {
  try {
    await store.updateTaskStatus(taskId, masteryLevel)
    const taskIndex = store.planTasks.findIndex(t => t.id === taskId)
    if (taskIndex !== -1) {
      store.planTasks[taskIndex].mastery_level = masteryLevel
    }
  } catch (error) {
    showToast('更新任务状态失败')
  }
}

function navigateToNoteHistory(noteId: number) {
  router.push(`/handbooks/notes/${noteId}/history`)
}

// 获取状态对应的类型
function getStatusType(status: string) {
  const typeMap = {
    mastered: 'success',
    partially_mastered: 'warning',
    not_mastered: 'danger'
  }
  return typeMap[status as keyof typeof typeMap] || 'danger'
}

// 获取状态对应的图标
function getStatusIcon(status: string) {
  const iconMap = {
    mastered: 'checked',
    partially_mastered: 'warning-o',
    not_mastered: 'clock-o'
  }
  return iconMap[status as keyof typeof iconMap] || 'question-o'
}

// 获取��态对应的文本
function getStatusText(status: string) {
  const textMap = {
    mastered: '已掌握',
    partially_mastered: '部分掌握',
    not_mastered: '未掌握'
  }
  return textMap[status as keyof typeof textMap] || '未知'
}
</script>

<template>
  <div class="plan-detail">
    <van-nav-bar
      :title="planDetails.name"
      left-arrow
      @click-left="router.back()"
    />
    
    <div class="detail-content">
      <!-- Plan Overview -->
      <van-cell-group inset class="plan-overview">
        <van-cell title="计划进度">
          <template #value>
            <van-progress 
              :percentage="progress"
              :pivot-text="`${progress}%`"
            />
          </template>
        </van-cell>
        <van-cell title="计划时间">
          <template #value>
            {{ formattedStartDate }} 至 {{ formattedEndDate }}
          </template>
        </van-cell>
      </van-cell-group>

      <!-- Filters -->
      <van-cell-group inset class="filters">
        <van-field
          v-model="filterDate"
          label="日期筛选"
          type="date"
          @change="handleFilterChange"
        />
        <van-cell title="状态筛选">
          <van-radio-group v-model="filterStatus" direction="horizontal" @change="handleFilterChange">
            <van-radio name="">全部</van-radio>
            <van-radio name="pending">待完成</van-radio>
            <van-radio name="completed">已完成</van-radio>
            <van-radio name="skipped">已跳过</van-radio>
          </van-radio-group>
        </van-cell>
      </van-cell-group>

      <!-- Task List -->
      <div v-if="store.planTasks.length" class="task-list">
        <div v-for="group in groupedTasks" :key="group.date" class="task-group">
          <div class="group-header">{{  formatISODate(group.date) }}</div>
          <van-cell-group inset>
            <van-cell
              v-for="task in group.tasks"
              :key="task.id"
              :title="task.note.title"
              is-link
              @click="handleTaskClick(task)"
            >
              <template #value>
                <div class="task-status">
                  <van-tag
                    :type="getStatusType(task.mastery_level)"
                    round
                    size="medium"
                    class="status-tag"
                  >
                    <van-icon :name="getStatusIcon(task.mastery_level)" class="status-icon" />
                    {{ getStatusText(task.mastery_level) }}
                  </van-tag>
                  <div 
                    class="history-btn-wrapper" 
                    @click.stop="navigateToNoteHistory(task.note.id)"
                  >
                    <van-badge 

                      max="99"
                      class="history-badge"
                    >
                      <div class="history-btn">
                        <van-icon name="chart-trending-o" class="history-icon" />
                        <span class="history-text">复习历史</span>
                      </div>
                    </van-badge>
                  </div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>
        </div>
      </div>
      
      <van-empty 
        v-else-if="!store.isLoading" 
        description="暂无任务" 
      />

      <!-- Loading State -->
      <div v-if="store.isLoading" class="loading-state">
        <van-loading type="spinner">加载中...</van-loading>
      </div>
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

    <div class="review-actions">
      <van-button 
        type="primary" 
        block 
        @click="router.push({ 
          name: 'revision-task-review', 
          query: { planId }
        })"
      >
        开始逐条复习
      </van-button>
      
      <van-button 
        type="success" 
        block 
        @click="router.push({ 
          name: 'revision-quick-review', 
          query: { planId }
        })"
      >
        快速复习模式
      </van-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.plan-detail {
  height: 100%;
  display: flex;
  flex-direction: column;

  .detail-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    
    .plan-overview,
    .filters {
      margin-bottom: 20px;
    }

    .task-group {
      margin-bottom: 20px;

      .group-header {
        padding: 0 16px;
        margin-bottom: 8px;
        font-size: 14px;
        color: var(--van-gray-6);
        font-weight: 500;
      }
    }

    .loading-state {
      display: flex;
      justify-content: center;
      padding: 20px 0;
    }

    .plan-overview {
      :deep(.van-cell__value) {
        display: flex;
        align-items: center;
        
        .van-progress {
          flex: 1;
        }
      }
    }

    .filters {
      :deep(.van-radio-group) {
        width: 100%;
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
      }
    }
  }
}

.review-actions {
  position: sticky;
  bottom: 0;
  padding: 16px;
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);
  
  display: flex;
  gap: 16px;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 8px;

  .status-tag {
    display: flex;
    align-items: center;
    padding: 2px 10px;
    font-size: 12px;
    
    .status-icon {
      margin-right: 4px;
      font-size: 14px;
    }
  }

  .history-btn {
    height: 24px;
    padding: 0 8px;
    font-size: 12px;
    border-radius: 12px;
    
    &:active {
      opacity: 0.8;
    }
    
    .van-icon {
      font-size: 14px;
      margin-right: 2px;
    }
  }
}

// 优化单元格样式
:deep(.van-cell) {
  align-items: center;
  padding: 12px 16px;
  
  &:active {
    background-color: var(--van-cell-active-color);
  }
}

.history-btn-wrapper {
  position: relative;
  cursor: pointer;
  
  .history-btn {
    display: flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 16px;
    background: var(--van-background-2);
    border: 1px solid var(--van-border-color);
    transition: all 0.2s ease;
    
    .history-icon {
      font-size: 16px;
      margin-right: 4px;
      color: var(--van-primary-color);
    }
    
    .history-text {
      font-size: 12px;
      color: var(--van-text-color);
    }
  }

  .history-badge {
    :deep(.van-badge) {
      transform: translate(50%, -50%);
      background: var(--van-primary-color);
    }
  }
  
  &:hover {
    .history-btn {
      background: var(--van-primary-color-light);
      border-color: var(--van-primary-color);
      
      .history-icon,
      .history-text {
        color: var(--van-primary-color);
      }
    }
  }
  
  &:active {
    .history-btn {
      transform: scale(0.95);
      background: var(--van-primary-color-dark);
      
      .history-icon,
      .history-text {
        color: var(--van-white);
      }
    }
  }
}
:deep{
  .van-cell__value{
    overflow: visible;
  }
}
// 暗色主题适配
:root[data-theme="dark"] {
  .history-btn-wrapper {
    .history-btn {
      background: var(--van-background);
      border-color: var(--van-gray-7);
      
      .history-text {
        color: var(--van-gray-5);
      }
    }
    
    &:hover .history-btn {
      background: var(--van-primary-color-dark);
      border-color: var(--van-primary-color);
      
      .history-icon,
      .history-text {
        color: var(--van-white);
      }
    }
  }
}
</style> 