<script setup lang="ts">
import { ref } from 'vue'
import { useHistoryStore } from '@/stores/history'

const store = useHistoryStore()
</script>

<template>
  <div class="learning-stats">
    <van-nav-bar
      title="学习统计"
      left-arrow
      @click-left="$router.back()"
    />
    <!-- 内容将在后续实现 -->
  </div>
</template>

<style lang="scss" scoped>
.learning-stats {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 