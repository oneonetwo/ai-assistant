<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { showToast } from 'vant'
import type { EChartsOption } from 'echarts'

const statisticsStore = useStatisticsStore()
const { masteryStats, isLoading } = storeToRefs(statisticsStore)

const progressChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()

// 初始化图表
function initCharts() {
  if (!masteryStats.value) return
  
  // 掌握进度环形图
  const progressChart = echarts.init(progressChartRef.value!)
  const progressOption: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['60%', '80%'],
      avoidLabelOverlap: false,
      label: {
        show: false
      },
      data: [
        { 
          value: masteryStats.value.mastered,
          name: '已掌握',
          itemStyle: { color: '#42b883' }
        },
        { 
          value: masteryStats.value.learning,
          name: '学习中',
          itemStyle: { color: '#4f46e5' }
        },
        { 
          value: masteryStats.value.struggling,
          name: '需加强',
          itemStyle: { color: '#ef4444' }
        }
      ]
    }]
  }
  progressChart.setOption(progressOption)

  // 分类分布柱状图
  const distributionChart = echarts.init(distributionChartRef.value!)
  const categories = Object.entries(masteryStats.value.category_distribution)
  const distributionOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: categories.map(([category]) => category),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '知识点数量'
    },
    series: [{
      type: 'bar',
      data: categories.map(([, count]) => count),
      itemStyle: {
        color: '#42b883'
      }
    }]
  }
  distributionChart.setOption(distributionOption)
}

onMounted(async () => {
  try {
    await statisticsStore.fetchMasteryStats()
    initCharts()
  } catch (error) {
    showToast('获取数据失败')
  }
})
</script>

<template>
  <div class="mastery-stats">
    <div class="stats-cards">
      <van-card>
        <template #title>知识点总数</template>
        <template #num>
          <span class="highlight">
            {{ masteryStats?.total_points || 0 }}
          </span>
          个
        </template>
      </van-card>

      <van-card>
        <template #title>掌握率</template>
        <template #num>
          <span class="highlight">
            {{ ((masteryStats?.mastery_rate || 0) * 100).toFixed(1) }}
          </span>
          %
        </template>
      </van-card>
    </div>

    <div class="charts">
      <div class="chart-container">
        <div class="chart-title">掌握进度</div>
        <div ref="progressChartRef" class="chart" />
        <div class="chart-legend">
          <div class="legend-item">
            <div class="color-block mastered" />
            <span>已掌握 ({{ masteryStats?.mastered || 0 }})</span>
          </div>
          <div class="legend-item">
            <div class="color-block learning" />
            <span>学习中 ({{ masteryStats?.learning || 0 }})</span>
          </div>
          <div class="legend-item">
            <div class="color-block struggling" />
            <span>需加强 ({{ masteryStats?.struggling || 0 }})</span>
          </div>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-title">分类分布</div>
        <div ref="distributionChartRef" class="chart" />
      </div>
    </div>

    <van-empty v-if="!masteryStats && !isLoading" description="暂无数据" />
    <van-loading v-if="isLoading" vertical>加载中...</van-loading>
  </div>
</template>

<style lang="scss" scoped>
.mastery-stats {
  padding: var(--van-padding-md);
  
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--van-padding-sm);
    margin-bottom: var(--van-padding-lg);
    
    .highlight {
      color: var(--van-primary-color);
      font-size: 24px;
      font-weight: bold;
    }
  }
  
  .charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--van-padding-lg);
    
    .chart-container {
      background: var(--van-background-2);
      border-radius: var(--van-radius-lg);
      padding: var(--van-padding-md);
      
      .chart-title {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: var(--van-padding-sm);
      }
      
      .chart {
        height: 300px;
      }
      
      .chart-legend {
        display: flex;
        justify-content: center;
        gap: var(--van-padding-md);
        margin-top: var(--van-padding-sm);
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: var(--van-padding-sm);
          
          .color-block {
            width: 12px;
            height: 12px;
            border-radius: 2px;
          }
          
          .mastered {
            background-color: #42b883;
          }
          
          .learning {
            background-color: #4f46e5;
          }
          
          .struggling {
            background-color: #ef4444;
          }
        }
      }
    }
  }
}
</style> 