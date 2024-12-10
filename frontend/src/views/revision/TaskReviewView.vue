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
      // 取计划的待复习任务  日期为今日
      planTasks = await store.fetchPlanTasks(planId, {
        status: 'pending',
        // date: new Date().toISOString()
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
  background-color: var(--van-background);
  
  :deep {
    .van-nav-bar {
      background: var(--van-background-2);
      border-bottom: 1px solid var(--van-border-color);
      
      .van-nav-bar__title {
        font-size: 18px;
        font-weight: 600;
        color: var(--van-text-color);
      }
      
      .van-icon {
        color: var(--van-text-color);
      }
    }
  }

  .progress-text {
    font-size: 14px;
    color: var(--van-primary-color);
    font-weight: 500;
  }

  .review-content {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: var(--van-background);
    position: relative;
    
    // 添加书本效果
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(to right, 
        rgba(0, 0, 0, 0.03) 0px,
        transparent 1px
      ) 0 0;
      background-size: 20px 100%;
      pointer-events: none;
    }
    
    // 任务卡片样式
    :deep {
      .task-card {
        background: var(--van-background-2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--van-border-color);
        
        .van-button {
          height: 40px;
          font-size: 14px;
          font-weight: 500;
          border-radius: 8px;
          margin: 0 8px;
          transition: all 0.3s ease;
          
          // 查看内容按钮
          &--view {
            background: var(--van-primary-color);
            border-color: var(--van-primary-color);
            color: white;
            
            &:active {
              opacity: 0.8;
            }
          }
          
          // 不熟悉按钮
          &--not-mastered {
            background: rgba(var(--van-danger-color), 0.1);
            border-color: var(--van-danger-color);
            color: var(--van-danger-color);
            
            &:active {
              background: rgba(var(--van-danger-color), 0.2);
            }
          }
          
          // 学习中按钮
          &--learning {
            background: rgba(var(--van-warning-color), 0.1);
            border-color: var(--van-warning-color);
            color: var(--van-warning-color);
            
            &:active {
              background: rgba(var(--van-warning-color), 0.2);
            }
          }
          
          // 已掌握按钮
          &--mastered {
            background: rgba(var(--van-success-color), 0.1);
            border-color: var(--van-success-color);
            color: var(--van-success-color);
            
            &:active {
              background: rgba(var(--van-success-color), 0.2);
            }
          }
        }
        
        .van-tag {
          padding: 4px 8px;
          font-size: 12px;
          font-weight: 500;
          border-radius: 6px;
          margin-right: 8px;
          
          // 复习次数标签
          &--primary {
            background: var(--van-primary-color);
            color: white;
            border: none;
          }
          
          // 掌握程度标签
          &--success {
            background: rgba(var(--van-success-color), 0.1);
            color: var(--van-success-color);
            border: 1px solid var(--van-success-color);
          }
          
          &--warning {
            background: rgba(var(--van-warning-color), 0.1);
            color: var(--van-warning-color);
            border: 1px solid var(--van-warning-color);
          }
          
          &--danger {
            background: rgba(var(--van-danger-color), 0.1);
            color: var(--van-danger-color);
            border: 1px solid var(--van-danger-color);
          }
        }
      }
    }
  }
}

// 深色主题
:root[data-theme="dark"] {
  .task-review {
    background: var(--van-black);
    
    .review-content {
      &::before {
        background: linear-gradient(to right, 
          rgba(255, 255, 255, 0.03) 0px,
          transparent 1px
        ) 0 0;
      }
      
      :deep {
        .task-card {
          background: var(--van-background-2);
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
          
          .van-button {
            &--not-mastered,
            &--learning,
            &--mastered {
              background: transparent;
            }
            
            &:active {
              opacity: 0.8;
            }
          }
          
          .van-tag {
            &--success,
            &--warning,
            &--danger {
              background: transparent;
            }
          }
        }
      }
    }
  }
}

// 浅色主题
:root[data-theme="light"] {
  .task-review {
    background: var(--van-white);
    
    .review-content {
      &::before {
        background: linear-gradient(to right, 
          rgba(0, 0, 0, 0.03) 0px,
          transparent 1px
        ) 0 0;
      }
      
      :deep {
        .task-card {
          background: var(--van-white);
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        }
      }
    }
  }
}
</style> 