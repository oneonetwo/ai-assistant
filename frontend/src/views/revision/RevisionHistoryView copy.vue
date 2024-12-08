<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useHistoryStore } from '@/stores/history'
import { showToast } from 'vant'
import HistoryTimeline from '@/components/revision/HistoryTimeline.vue'
import StatisticsChart from '@/components/revision/StatisticsChart.vue'

const route = useRoute()
const store = useHistoryStore()
const activeTab = ref(0)

const noteId = Number(route.params.noteId)

onMounted(async () => {
  if (!noteId) return
  
  try {
    await Promise.all([
      store.fetchNoteHistory(noteId),
      store.fetchNoteStatistics(noteId)
    ])
  } catch (error) {
    showToast('获取历史记录失败')
  }
})
</script>

<template>
  <div class="revision-history">
    <van-nav-bar
      title="复习历史"
      left-arrow
      @click-left="$router.back()"
    />
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="历史记录">
        <HistoryTimeline 
          v-if="store.noteHistory.length"
          :histories="store.noteHistory"
        />
        <van-empty v-else description="暂无历史记录" />
      </van-tab>
      
      <van-tab title="统计分析">
        <div class="statistics-content" v-if="store.noteStatistics">
          <div class="stats-card">
            <div class="stats-item">
              <span class="label">总复习次数</span>
              <span class="value">{{ store.noteStatistics.total_revisions }}</span>
            </div>
            
            <div class="stats-item">
              <span class="label">掌握程度</span>
              <van-progress
                :percentage="
                  (store.noteStatistics.mastery_levels.high || 0) * 100 / 
                  Object.values(store.noteStatistics.mastery_levels).reduce((a, b) => a + b, 0)
                "
                color="#07c160"
              />
            </div>
          </div>
          
          <StatisticsChart :statistics="store.noteStatistics" />
        </div>
        <van-empty v-else description="暂无统计数据" />
      </van-tab>
    </van-tabs>
  </div>
</template>

<style lang="scss" scoped>
.revision-history {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .statistics-content {
    padding: 16px;
    
    .stats-card {
      background: var(--van-background-2);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      
      .stats-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .label {
          width: 80px;
          font-size: 14px;
          color: var(--van-text-color-2);
        }
        
        .value {
          font-size: 20px;
          font-weight: 500;
          color: var(--van-text-color);
        }
      }
    }
  }
}
</style> 