<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'

const router = useRouter()

function navigateToPlans() {
  router.push({ name: 'revision-plans' })
}

function navigateToDailyTasks() {
  router.push({ name: 'revision-tasks' })
}
</script>

<template>
  <div class="revision-view">
    <van-nav-bar
      title="复习"
      right-text="设置"
      @click-right="$router.push('/revision/settings')"
    />
    <AppHeader title="复习计划管理" />
    <router-view v-slot="{ Component }">
      <component :is="Component" />
    </router-view>
  </div>
</template>

<style lang="scss" scoped>
.revision-view {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.app-header) {
    flex-shrink: 0;
  }

  .router-view-container {
    flex: 1;
    overflow-y: auto;
  }
}
</style> 