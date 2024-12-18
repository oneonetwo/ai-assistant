<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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

// 计算掌握度百分比的方法
const calculateMasteryPercentage = computed(() => {
  if (!store.noteStatistics?.mastery_levels) return 0
  
  const levels = store.noteStatistics.mastery_levels
  const total = Object.values(levels).reduce((a, b) => a + b, 0)
  if (total === 0) return 0
  
  // 加权计算：高掌握 = 1.0, 中等 = 0.6, 低 = 0.2
  const weightedScore = (
    (levels.high || 0) * 1.0 + 
    (levels.medium || 0) * 0.6 + 
    (levels.low || 0) * 0.2
  ) / total
  
  return Math.round(weightedScore * 100)
})

// 掌握度数据
const masteryLevels = computed(() => ({
  high: store.noteStatistics?.mastery_levels.high || 0,
  medium: store.noteStatistics?.mastery_levels.medium || 0,
  low: store.noteStatistics?.mastery_levels.low || 0
}))
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
            
            <div class="stats-item mastery-item">
              <span class="label">掌握程度</span>
              <div class="mastery-content">
                <van-progress
                  :percentage="calculateMasteryPercentage"
                  :stroke-width="8"
                  :show-pivot="false"
                >
                  <template #bottom>
                    <div class="mastery-details">
                      <span class="mastery-level">
                        <span class="dot high"></span>
                        高掌握 {{ masteryLevels.high }}次
                      </span>
                      <span class="mastery-level">
                        <span class="dot medium"></span>
                        中等 {{ masteryLevels.medium }}次
                      </span>
                      <span class="mastery-level">
                        <span class="dot low"></span>
                        待加强 {{ masteryLevels.low }}次
                      </span>
                    </div>
                  </template>
                </van-progress>
              </div>
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
  
  .mastery-item {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px;
    
    .mastery-content {
      width: 100%;
      
      :deep{
        .van-progress{
        margin-bottom: 8px;
        
        &__portion {
          background: linear-gradient(to right, #07c160, #2ecc71);
        }
      }
      }
    }
  }
}

.mastery-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--van-text-color-2);
  margin-top: 4px;
  
  .mastery-level {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      
      &.high {
        background-color: #07c160;
      }
      
      &.medium {
        background-color: #ff976a;
      }
      
      &.low {
        background-color: #ee0a24;
      }
    }
  }
}
</style> 