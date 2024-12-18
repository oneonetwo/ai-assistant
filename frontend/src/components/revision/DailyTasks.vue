<script setup lang="ts">
import { onMounted } from 'vue'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { RevisionTask } from '@/types/revision'

const store = useRevisionStore()

onMounted(async () => {
  try {
    await store.fetchDailyTasks()
  } catch (error) {
    showToast('加载每日任务失败')
  }
})

async function handleStatusChange(task: RevisionTask, status: RevisionTask['status']) {
  try {
    await store.updateTaskStatus(task.id, status)
  } catch (error) {
    showToast('更新任务状态失败')
  }
}
</script>

<template>
  <div class="daily-tasks">
    <div class="progress-header">
      <h3>今日复习进度</h3>
      <van-progress 
        :percentage="store.progress"
        :pivot-text="`${store.completedTasksCount}/${store.totalTasksCount}`"
      />
    </div>

    <div class="task-list">
      <van-cell-group v-if="store.dailyTasks.length">
        <van-cell
          v-for="task in store.dailyTasks"
          :key="task.id"
          :title="task.title"
        >
          <template #right-icon>
            <van-button-group>
              <van-button 
                size="small"
                :type="task.status === 'not_mastered' ? 'danger' : ''"
                @click="handleStatusChange(task, 'not_mastered')"
              >
                未掌握
              </van-button>
              <van-button
                size="small"
                :type="task.status === 'partially_mastered' ? 'warning' : ''"
                @click="handleStatusChange(task, 'partially_mastered')"
              >
                部分掌握
              </van-button>
              <van-button
                size="small"
                :type="task.status === 'mastered' ? 'success' : ''"
                @click="handleStatusChange(task, 'mastered')"
              >
                已掌握
              </van-button>
            </van-button-group>
          </template>
        </van-cell>
      </van-cell-group>

      <van-empty v-else description="今日暂无复习任务" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.daily-tasks {
  padding: 16px;

  .progress-header {
    margin-bottom: 20px;

    h3 {
      margin-bottom: 8px;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .task-list {
    .van-button-group {
      display: flex;
      gap: 4px;
    }
  }
}
</style> 