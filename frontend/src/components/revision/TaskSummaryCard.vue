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
        icon: 'warning-o',
        background: 'var(--van-danger-color)'
      }
    case 'upcoming':
      return {
        color: 'var(--van-primary-color)',
        icon: 'clock-o',
        background: 'var(--van-primary-color)'
      }
    case 'completed':
      return {
        color: 'var(--van-success-color)',
        icon: 'checked',
        background: 'var(--van-success-color)'
      }
  }
})
</script>

<template>
  <div 
    class="task-summary-card"
    :class="type"
  >
    <div class="icon-wrapper">
      <van-icon 
        :name="typeConfig.icon" 
        :color="typeConfig.color"
        size="24"
      />
    </div>
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
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: currentColor;
    opacity: 0.1;
  }
  
  .icon-wrapper {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: var(--van-background-3);
  }
  
  .card-content {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title {
      font-size: 16px;
      font-weight: 500;
      color: var(--van-text-color);
    }
    
    .count {
      font-size: 24px;
      font-weight: 600;
    }
  }
  
  &.pending {
    color: var(--van-danger-color);
  }
  
  &.upcoming {
    color: var(--van-primary-color);
  }
  
  &.completed {
    color: var(--van-success-color);
  }
}
</style> 