<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionTask } from '@/types/revision'
import { formatDate } from '@/utils/date'
import TaskExecution from '@/components/revision/TaskExecution.vue'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()
const showTaskExecution = ref(false)
const currentTask = ref<RevisionTask | null>(null)

// 筛选条件
const filterDate = ref('')
const filterStatus = ref<'pending' | 'completed' | 'skipped' | ''>('')

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
            {{ planDetails.start_date }} 至 {{ planDetails.end_date }}
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
          <div class="group-header">{{ group.date }}</div>
          <van-cell-group inset>
            <van-cell
              v-for="task in group.tasks"
              :key="task.id"
              :title="task.note.title"
              is-link
              @click="handleTaskClick(task)"
            >
              <template #value>
                <van-tag
                  :type="task.status === 'mastered' ? 'success' : 
                         task.status === 'partially_mastered' ? 'warning' : 'danger'"
                  round
                >
                  {{ task.status === 'mastered' ? '已掌握' :
                     task.status === 'partially_mastered' ? '部分掌握' : '未掌握' }}
                </van-tag>
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
</style> 