<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'

const route = useRoute()

// 根据路由获取标题
const title = computed(() => {
  return route.meta.title as string
})
</script>

<template>
  <div class="handbook-layout">
    <AppHeader :title="title" :show-back="route.name !== 'handbooks'" />
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style lang="scss" scoped>
.handbook-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--van-background);
  
  .main-content {
    flex: 1;
    overflow-y: auto;
  }
}
</style> 