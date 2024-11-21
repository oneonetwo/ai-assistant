<script setup lang="ts">
defineProps<{
  count?: number
}>()
</script>

<template>
  <div 
    v-for="i in (count || 3)" 
    :key="i"
    class="message-skeleton"
    :style="{
      animationDelay: `${i * 0.1}s`
    }"
  >
    <div class="avatar-skeleton" />
    <div class="content-skeleton">
      <div 
        class="text-line" 
        v-for="j in (i % 2 ? 2 : 3)" 
        :key="j"
        :style="{ width: `${Math.random() * 30 + 60}%` }"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.message-skeleton {
  display: flex;
  gap: 12px;
  padding: 16px;
  animation: skeleton-fade 1s ease-in-out infinite alternate;
}

.avatar-skeleton {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  background: var(--van-skeleton-color);
}

.content-skeleton {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.text-line {
  height: 16px;
  background: var(--van-skeleton-color);
  border-radius: 4px;
}

@keyframes skeleton-fade {
  from {
    opacity: 0.6;
  }
  to {
    opacity: 1;
  }
}
</style> 