<script setup lang="ts">
import { onMounted } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import HandbookList from '@/components/handbook/HandbookList.vue'

const store = useHandbookStore()

onMounted(async () => {
  await store.fetchHandbooks()
})
</script>

<template>
  <div class="handbook-list-view">
    <HandbookList />
  </div>
</template>

<style lang="scss" scoped>
.handbook-list-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 