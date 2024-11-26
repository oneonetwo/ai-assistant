<template>
  <div class="upload-progress">
    <div class="progress-bar">
      <div 
        class="progress-inner" 
        :style="{ width: `${progress}%` }"
      />
    </div>
    <div class="progress-info">
      <span>{{ progress }}%</span>
      <van-button 
        size="mini" 
        type="danger" 
        @click="$emit('cancel')"
      >
        取消
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  progress: number
}>()

defineEmits<{
  (e: 'cancel'): void
}>()
</script>

<style lang="scss" scoped>
.upload-progress {
  margin: 8px 0;
  
  .progress-bar {
    height: 4px;
    background: var(--van-gray-3);
    border-radius: 2px;
    overflow: hidden;
    
    .progress-inner {
      height: 100%;
      background: var(--van-primary-color);
      transition: width 0.2s;
    }
  }
  
  .progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
    font-size: 12px;
    color: var(--van-gray-6);
  }
}
</style> 