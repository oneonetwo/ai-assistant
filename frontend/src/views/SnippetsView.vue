<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CodeSnippets from '@/components/chat/CodeSnippets.vue'

const router = useRouter()
</script>

<template>
  <div class="snippets-view">
    <van-nav-bar
      title="代码片段"
      left-arrow
      @click-left="router.back()"
    />
    
    <div class="snippets-container">
      <CodeSnippets />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.snippets-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.snippets-container {
  flex: 1;
  overflow-y: auto;
}
</style> 