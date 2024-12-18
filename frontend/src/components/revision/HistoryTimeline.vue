<script setup lang="ts">
import { computed } from 'vue'
import type { RevisionHistory } from '@/types/history'
import { formatDate } from '@/utils/date'

const props = defineProps<{
  histories: RevisionHistory[]
}>()

const groupedHistories = computed(() => {
  const groups: Record<string, RevisionHistory[]> = {}
  props.histories.forEach(history => {
    const date = formatDate(history.revision_date, 'YYYY-MM-DD')
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(history)
  })
  return groups
})

const masteryLevelConfig = {
  high: {
    color: 'var(--van-success-color)',
    text: '已掌握'
  },
  medium: {
    color: 'var(--van-warning-color)',
    text: '待巩固'
  },
  low: {
    color: 'var(--van-danger-color)',
    text: '需复习'
  }
}
</script>

<template>
  <div class="history-timeline">
    <template v-for="(histories, date) in groupedHistories" :key="date">
      <div class="timeline-date">{{ formatDate(date, 'MM月DD日') }}</div>
      <div class="timeline-items">
        <div 
          v-for="history in histories" 
          :key="history.id"
          class="timeline-item"
        >
          <div class="time">{{ formatDate(history.revision_date, 'HH:mm') }}</div>
          <div class="content">
            <div class="mastery-level" :style="{ color: masteryLevelConfig[history.mastery_level as keyof typeof masteryLevelConfig]?.color }">
              {{ masteryLevelConfig[history.mastery_level as keyof typeof masteryLevelConfig]?.text }}
            </div>
            <div class="comments" v-if="history.comments">{{ history.comments }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.history-timeline {
  padding: 16px;

  .timeline-date {
    font-size: 14px;
    color: var(--van-text-color-2);
    margin: 16px 0 8px;
    
    &:first-child {
      margin-top: 0;
    }
  }

  .timeline-items {
    .timeline-item {
      display: flex;
      gap: 12px;
      padding: 12px;
      background: var(--van-background-2);
      border-radius: 8px;
      margin-bottom: 8px;

      .time {
        font-size: 14px;
        color: var(--van-text-color-3);
        min-width: 48px;
      }

      .content {
        flex: 1;

        .mastery-level {
          font-weight: 500;
          margin-bottom: 4px;
        }

        .comments {
          font-size: 14px;
          color: var(--van-text-color-2);
        }
      }
    }
  }
}
</style> 