<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import StudyTimeStats from './StudyTimeStats.vue'
import MasteryStats from './MasteryStats.vue'
import RevisionStats from './RevisionStats.vue'
import TagStats from './TagStats.vue'

const statisticsStore = useStatisticsStore()

onMounted(async () => {
  await statisticsStore.fetchOverallStats()
})
</script>

<template>
  <div class="statistics-overview">
    <study-time-stats class="stats-section" />
    <mastery-stats class="stats-section" />
    <revision-stats class="stats-section" />
    <tag-stats class="stats-section" />
  </div>
</template>

<style lang="scss" scoped>
.statistics-overview {
  padding: var(--van-padding-md);
  
  .stats-section {
    margin-bottom: var(--van-padding-lg);
  }
}
</style> 