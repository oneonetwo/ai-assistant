<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionPlan } from '@/types/revision'

const router = useRouter()
const store = useRevisionStore()
const currentStatus = ref<string>('active')

const statusOptions = [
  { text: '进行中', value: 'active' },
  { text: '已完成', value: 'completed' },
  { text: '已取消', value: 'cancelled' }
]

async function fetchPlans(status: string) {
  try {
    await store.fetchPlans({ status })
  } catch (error) {
    showToast('加载复习计划失败')
  }
}

onMounted(() => {
  fetchPlans(currentStatus.value)
})

async function handleStatusChange(status: string) {
  currentStatus.value = status
  await fetchPlans(status)
}

function handleCreatePlan() {
  router.push({ name: 'revision-plan-new' })
}

function handlePlanClick(plan: RevisionPlan) {
  router.push({ 
    name: 'revision-plan-detail',
    params: { id: plan.id }
  })
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

function calculateDuration(start: string, end: string): number {
  const startDate = new Date(start)
  const endDate = new Date(end)
  return Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
}
</script>

<template>
  <div class="revision-plan-list">
    <van-nav-bar title="我的计划列表">
      <template #right>
        <van-button 
          type="primary" 
          size="small"
          @click="handleCreatePlan"
        >
          新建计划
        </van-button>
      </template>
    </van-nav-bar>

    <div class="filter-section">
      <van-tabs v-model:active="currentStatus" @change="handleStatusChange">
        <van-tab 
          v-for="option in statusOptions"
          :key="option.value"
          :name="option.value"
          :title="option.text"
        />
      </van-tabs>
    </div>

    <div class="plan-list" v-if="store.plans.length">
      <van-cell-group>
        <van-cell
          v-for="plan in store.plans"
          :key="plan.id"
          :title="plan.name"
          is-link
          @click="handlePlanClick(plan)"
        >
          <template #label>
            <div class="plan-info">
              <div class="date-range">
                {{ formatDate(plan.start_date) }} - {{ formatDate(plan.end_date) }}
              </div>
              <div class="duration">
                {{ calculateDuration(plan.start_date, plan.end_date) }}天
              </div>
              <van-tag :type="plan.status === 'active' ? 'primary' : 'default'">
                {{ plan.status === 'active' ? '进行中' : 
                   plan.status === 'completed' ? '已完成' : '已取消' }}
              </van-tag>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div v-else class="empty-state">
      <van-empty description="暂无复习计划" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.revision-plan-list {
  height: 100%;
  display: flex;
  flex-direction: column;

  .plan-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;

    :deep(.van-cell-group) {
      background: transparent;
    }

    :deep(.van-cell) {
      margin-bottom: 12px;
      border-radius: 8px;
      background: var(--van-background);
      
      &::after {
        display: none;
      }
    }
  }

  .plan-info {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 4px;
    font-size: 14px;
    color: var(--van-gray-6);

    .date-range {
      flex: 1;
    }

    .duration {
      white-space: nowrap;
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .filter-section {
    position: sticky;
    top: 0;
    z-index: 1; :deep {
      .van-tabs__wrap {
        height: 44px;
      }

      .van-tab {
        color: var(--van-text-color-2);
        font-size: 14px;
        
        &--active {
          color: var(--van-primary-color);
          font-weight: 500;
        }
      }

      .van-tabs__line {
        background-color: var(--van-primary-color);
      }
    }
    background: var(--van-background);
    border-bottom: 1px solid var(--van-border-color);
  }
}

// 深色主题适配
:root[data-theme="dark"] {
  .plan-list {
    :deep {
      .van-cell {
        background: var(--van-background-2);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        border: 1px solid var(--van-gray-8);
        
        &:hover {
          border-color: var(--van-primary-color);
          transform: translateY(-1px);
          transition: all 0.3s ease;
        }
      }
    }
  }
}
</style> 