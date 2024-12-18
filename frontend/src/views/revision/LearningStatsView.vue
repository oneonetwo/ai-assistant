<script setup lang="ts">
import { ref } from 'vue'
import { useHistoryStore } from '@/stores/history'

const store = useHistoryStore()
</script>

<template>
  <div class="learning-stats">
    <van-nav-bar
      title="学习统计"
      left-arrow
      @click-left="$router.back()"
    />
    <!-- 最近复习的笔记 -->
    <div class="recent-notes">
      <h3>最近复习的笔记</h3>
      <van-cell-group>
        <van-cell
          v-for="note in recentNotes"
          :key="note.id"
          :title="note.title"
          :label="formatDate(note.lastReviewAt)"
          is-link
          @click="router.push(`/handbook/notes/${note.id}/history`)"
        />
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.learning-stats {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 