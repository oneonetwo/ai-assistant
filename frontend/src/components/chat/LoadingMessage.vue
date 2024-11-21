<script setup lang="ts">
import { ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'

const dots = ref('.')

useIntervalFn(() => {
  dots.value = dots.value.length >= 3 ? '.' : dots.value + '.'
}, 500)
</script>

<template>
  <div class="loading-message">
    <div class="loading-avatar">
      <van-image
        src="/avatar-assistant.png"
        width="40"
        height="40"
        radius="4"
      />
    </div>
    <div class="loading-content">
      <span class="typing-dots">
        AI思考中{{ dots }}
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.loading-message {
  display: flex;
  padding: var(--van-padding-sm);
  gap: var(--van-padding-sm);
  animation: slide-up 0.3s ease-out;
}

.loading-avatar {
  flex-shrink: 0;
}

.loading-content {
  display: flex;
  align-items: center;
  padding: var(--van-padding-sm);
  background-color: var(--van-background-2);
  border-radius: var(--van-radius-lg);
}
</style> 