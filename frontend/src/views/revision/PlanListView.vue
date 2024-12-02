<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionPlan } from '@/types/revision'

const router = useRouter()
const store = useRevisionStore()

onMounted(async () => {
  try {
    await store.fetchPlans()
  } catch (error) {
    showToast('加载复习计划失败')
  }
})

function handleCreatePlan() {
  router.push({ name: 'revision-plan-new' })
}

function handlePlanClick(plan: RevisionPlan) {
  router.push({ 
    name: 'revision-plan-detail',
    params: { id: plan.id }
  })
}
</script>

<template>
  <div class="revision-plan-list">
    <van-nav-bar title="复习计划">
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

    <div class="plan-list" v-if="store.plans.length">
      <van-cell-group>
        <van-cell
          v-for="plan in store.plans"
          :key="plan.id"
          :title="plan.title"
          is-link
          @click="handlePlanClick(plan)"
        >
          <template #label>
            <div class="plan-info">
              <span class="duration">{{ plan.duration }}天</span>
              <van-tag 
                :type="plan.priority === 'high' ? 'danger' : 
                       plan.priority === 'medium' ? 'warning' : 'success'"
              >
                {{ plan.priority === 'high' ? '高优先级' :
                   plan.priority === 'medium' ? '中优先级' : '低优先级' }}
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
  }

  .plan-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 4px;

    .duration {
      color: var(--van-gray-6);
      font-size: 14px;
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style> 