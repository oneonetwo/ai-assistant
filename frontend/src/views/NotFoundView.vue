<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <van-empty
      image="error"
      description="页面不存在"
    >
      <template #bottom>
        <van-button
          round
          type="primary"
          @click="router.push('/')"
        >
          返回首页
        </van-button>
      </template>
    </van-empty>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--van-padding-md);
}
</style> 