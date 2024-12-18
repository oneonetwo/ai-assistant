<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionHistory } from '@/types/revision'

const props = defineProps<{
  taskId: number
}>()

const store = useRevisionStore()
const history = ref<RevisionHistory[]>([])

async function loadHistory() {
  try {
    history.value = await store.getTaskHistory(props.taskId)
  } catch (error) {
    showToast('加载历史记录失败')
  }
}

onMounted(loadHistory)

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
}
</script>

<template>
  <div class="task-history">
    <van-cell-group title="复习历史">
      <template v-if="history.length">
        <van-cell 
          v-for="record in history" 
          :key="record.id"
        >
          <template #title>
            <div class="history-item">
              <span class="date">
                {{ new Date(record.revision_date).toLocaleDateString() }}
              </span>
              <van-tag 
                :type="record.mastery_level === 'mastered' ? 'success' : 
                       record.mastery_level === 'partially_mastered' ? 'warning' : 'danger'"
              >
                {{ record.mastery_level === 'mastered' ? '已掌握' :
                   record.mastery_level === 'partially_mastered' ? '部分掌握' : '未掌握' }}
              </van-tag>
            </div>
          </template>
          <template #label>
            <div class="history-detail">
              <span>模式: {{ record.revision_mode === 'quick' ? '快速' : '普通' }}</span>
              <span v-if="record.time_spent">
                用时: {{ formatDuration(record.time_spent) }}
              </span>
              <div v-if="record.comments" class="comments">
                备注: {{ record.comments }}
              </div>
            </div>
          </template>
        </van-cell>
      </template>
      <van-empty v-else description="暂无复习记录" />
    </van-cell-group>
  </div>
</template>

<style lang="scss" scoped>
.task-history {
  .history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .history-detail {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    color: var(--van-gray-6);

    .comments {
      margin-top: 4px;
    }
  }
}
</style> 