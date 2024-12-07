<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRevisionStore } from '@/stores/revision'
import type { RevisionPlan } from '@/types/revision'
import { showToast } from 'vant'

const props = defineProps<{
  handbookId: number
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'select', plan: RevisionPlan): void
}>()

const revisionStore = useRevisionStore()
const plans = ref<RevisionPlan[]>([])
const selectedPlanId = ref<number>()

async function loadPlans() {
  try {
    plans.value = await revisionStore.checkHandbookPlans(props.handbookId)
  } catch (error) {
    showToast('获取复习计划失败')
  }
}

function handleSelect(plan: RevisionPlan) {
  selectedPlanId.value = plan.id
  emit('select', plan)
  emit('update:show', false)
}

onMounted(() => {
  if (props.show) {
    loadPlans()
  }
})
</script>

<template>
  <van-popup
:show="show"
    position="bottom"
    round
    closeable
  >
    <div class="plan-selector">
      <div class="header">
        <h3>选择复习计划</h3>
      </div>
      <div class="plans">
        <van-radio-group v-model="selectedPlanId">
          <van-cell-group>
            <van-cell
              v-for="plan in plans"
              :key="plan.id"
              :title="plan.name"
              clickable
              @click="handleSelect(plan)"
            >
              <template #right-icon>
                <van-radio :name="plan.id" />
              </template>
            </van-cell>
          </van-cell-group>
        </van-radio-group>
      </div>
    </div>
  </van-popup>
</template>

<style lang="scss" scoped>
.plan-selector {
  padding: 16px;
  
  .header {
    margin-bottom: 16px;
    text-align: center;
    
    h3 {
      margin: 0;
      font-size: 16px;
    }
  }
}
</style> 