<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DailyTasks from '@/components/revision/DailyTasks.vue'
import TaskExecution from '@/components/revision/TaskExecution.vue'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import { ref } from 'vue'
import type { RevisionTask } from '@/types/revision'

const router = useRouter()
const store = useRevisionStore()
const currentTask = ref<RevisionTask | null>(null)
const showExecution = ref(false)

onMounted(async () => {
  try {
    await store.fetchDailyTasks()
  } catch (error) {
    showToast('加载任务失败')
  }
})

function handleTaskClick(task: RevisionTask) {
  currentTask.value = task
  showExecution.value = true
}

async function handleStatusChange(status: RevisionTask['status']) {
  if (!currentTask.value) return
  
  try {
    await store.updateTaskStatus(currentTask.value.id, status)
    showExecution.value = false
    currentTask.value = null
  } catch (error) {
    showToast('更新状态失败')
  }
}
</script>

<template>
  <div class="task-list-view">
    <van-nav-bar 
      title="今日复习任务"
      left-arrow
      @click-left="router.back()"
    />

    <div class="task-content">
      <DailyTasks @task-click="handleTaskClick" />
    </div>

    <!-- 任务执行弹窗 -->
    <van-popup
      v-model:show="showExecution"
      position="bottom"
      :style="{ height: '70%' }"
      round
    >
      <TaskExecution
        v-if="currentTask"
        :task="currentTask"
        @status-change="handleStatusChange"
      />
    </van-popup>
  </div>
</template>

<style lang="scss" scoped>
.task-list-view {
  height: 100%;
  display: flex;
  flex-direction: column;

  .task-content {
    flex: 1;
    overflow-y: auto;
  }
}
</style> 