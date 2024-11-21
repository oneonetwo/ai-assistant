<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

const error = ref<Error | null>(null)
const router = useRouter()

onErrorCaptured((err) => {
  error.value = err as Error
  return false // 阻止错误继续传播
})

function handleReload() {
  error.value = null
  window.location.reload()
}

function handleBack() {
  error.value = null
  router.back()
}
</script>

<template>
  <template v-if="error">
    <div class="error-boundary">
      <van-empty
        image="error"
        :description="error.message || '页面出现错误'"
      >
        <template #bottom>
          <div class="error-actions">
            <van-button 
              type="primary" 
              size="small"
              @click="handleReload"
            >
              重新加载
            </van-button>
            <van-button
              plain
              size="small"
              @click="handleBack"
            >
              返回上页
            </van-button>
          </div>
        </template>
      </van-empty>
    </div>
  </template>
  <template v-else>
    <slot />
  </template>
</template>

<style lang="scss" scoped>
.error-boundary {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--van-padding-md);
}

.error-actions {
  display: flex;
  gap: var(--van-padding-sm);
  margin-top: var(--van-padding-sm);
}
</style> 