<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { RevisionAPI } from '@/services/revisionService'
import { showToast } from 'vant'
import type { RevisionTask } from '@/types/revision'

const route = useRoute()
const router = useRouter()
const store = useRevisionStore()
const planTasks = ref<RevisionTask[]>([])

const planId = Number(route.params.id)
const planDetails = ref({
  name: '',
  start_date: '',
  end_date: '',
  status: ''
})

onMounted(async () => {
  try {
    const plan = await RevisionAPI.getPlan(planId)
    planDetails.value = plan
    const tasks = await RevisionAPI.getPlanTasks(planId)
    planTasks.value = tasks
  } catch (error) {
    showToast('加载计划详情失败')
    router.back()
  }
})

async function handleTaskStatusChange(task: RevisionTask, status: RevisionTask['status']) {
  try {
    await store.updateTaskStatus(task.id, status)
    const index = planTasks.value.findIndex(t => t.id === task.id)
    if (index !== -1) {
      planTasks.value[index] = {
        ...planTasks.value[index],
        status
      }
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
      <van-cell-group title="计划信息">
        <van-cell title="开始日期" :value="planDetails.start_date" />
        <van-cell title="结束日期" :value="planDetails.end_date" />
        <van-cell title="状态" :value="planDetails.status" />
      </van-cell-group>

      <van-cell-group title="任务列表">
        <van-cell
          v-for="task in planTasks"
          :key="task.id"
          :title="task.title"
        >
          <template #value>
            <van-tag
              :type="task.status === 'mastered' ? 'success' :
                     task.status === 'partially_mastered' ? 'warning' : 'danger'"
            >
              {{ task.status === 'mastered' ? '已掌握' :
                 task.status === 'partially_mastered' ? '部分掌握' : '未掌握' }}
            </van-tag>
          </template>
          <template #right-icon>
            <van-dropdown-menu>
              <van-dropdown-item
                v-model="task.status"
                :options="[
                  { text: '未掌握', value: 'not_mastered' },
                  { text: '部分掌握', value: 'partially_mastered' },
                  { text: '已掌握', value: 'mastered' }
                ]"
                @change="(value) => handleTaskStatusChange(task, value)"
              />
            </van-dropdown-menu>
          </template>
        </van-cell>
      </van-cell-group>
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

    .van-cell-group {
      margin-bottom: 16px;
    }
  }
}
</style> 