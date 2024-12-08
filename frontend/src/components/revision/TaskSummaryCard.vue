<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  count: number
  type: 'pending' | 'upcoming' | 'completed'
}>()

const typeConfig = computed(() => {
  switch (props.type) {
    case 'pending':
      return {
        color: 'var(--van-danger-color)',
        icon: 'warning-o'
      }
    case 'upcoming':
      return {
        color: 'var(--van-primary-color)',
        icon: 'clock-o'
      }
    case 'completed':
      return {
        color: 'var(--van-success-color)',
        icon: 'checked'
      }
  }
})
</script>

<template>
  <div class="task-summary-card">
    <van-icon 
      :name="typeConfig.icon" 
      :color="typeConfig.color"
      size="24"
    />
    <div class="card-content">
      <span class="title">{{ title }}</span>
      <span 
        class="count"
        :style="{ color: typeConfig.color }"
      >
        {{ count }}
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.task-summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--van-background-2);
  border-radius: 8px;
  
  .card-content {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title {
      font-size: 16px;
      font-weight: 500;
    }
    
    .count {
      font-size: 20px;
      font-weight: 600;
    }
  }
}
</style> 