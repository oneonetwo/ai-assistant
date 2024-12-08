<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import TaskSummaryCard from '@/components/revision/TaskSummaryCard.vue'

const store = useNotificationStore()
const router = useRouter()

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
      <div class="summary-cards">
        <TaskSummaryCard
          v-if="store.summary"
          title="待复习"
          :count="store.summary.pending_tasks"
          type="pending"
        />
        
        <TaskSummaryCard
          v-if="store.summary"
          title="即将到期"
          :count="store.summary.upcoming_tasks"
          type="upcoming"
        />
        
        <TaskSummaryCard
          v-if="store.summary"
          title="已完成"
          :count="store.summary.completed_tasks"
          type="completed"
        />
      </div>
      
      <div v-if="store.summary?.suggestions.length" class="suggestions">
        <h3>建议复习</h3>
        <van-cell-group inset>
          <van-cell
            v-for="item in store.summary.suggestions"
            :key="item.id"
            :title="item.title"
            is-link
            @click="router.push(`/revision/tasks/${item.id}`)"
          />
        </van-cell-group>
      </div>
      
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
    
    .summary-cards {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 24px;
    }
    
    .suggestions {
      margin-bottom: 24px;
      
      h3 {
        margin: 0 0 12px;
        padding: 0 12px;
        font-size: 16px;
        color: var(--van-text-color);
      }
    }
    
    .summary-actions {
      margin-top: auto;
      padding-top: 24px;
    }
  }
}
</style> 