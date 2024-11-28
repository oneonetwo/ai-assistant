<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TagManager from '@/components/handbook/TagManager.vue'
import { useHandbookStore } from '@/stores/handbook'

const router = useRouter()
const store = useHandbookStore()

onMounted(async () => {
  await store.fetchTags()
})
</script>

<template>
  <div class="tag-manager-view">
    <van-nav-bar
      title="标签管理"
      left-arrow
      @click-left="router.back()"
    />
    <TagManager />
  </div>
</template>

<style lang="scss" scoped>
.tag-manager-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 