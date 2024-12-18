<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { showToast } from 'vant'
import type { EChartsOption } from 'echarts'

const statisticsStore = useStatisticsStore()
const { tagStats, isLoading } = storeToRefs(statisticsStore)

const wordCloudRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()

// 初始化图表
function initCharts() {
  if (!tagStats.value) return
  
  // 标签词云图
  const wordCloudChart = echarts.init(wordCloudRef.value!)
  const wordCloudOption: EChartsOption = {
    tooltip: {
      show: true
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      right: null,
      bottom: null,
      sizeRange: [12, 36],
      rotationRange: [-45, 45],
      rotationStep: 45,
      gridSize: 8,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
        color: function () {
          return 'rgb(' + [
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160)
          ].join(',') + ')'
        }
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          shadowBlur: 10,
          shadowColor: '#333'
        }
      },
      data: tagStats.value.tags.map(tag => ({
        name: tag.name,
        value: tag.count,
        textStyle: {
          color: tag.color
        }
      }))
    }]
  }
  wordCloudChart.setOption(wordCloudOption)

  // 分类统计图
  const categoryChart = echarts.init(categoryChartRef.value!)
  const categoryOption: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '50%',
      data: tagStats.value.categories.map(category => ({
        name: category.name,
        value: category.count,
        itemStyle: { color: category.color }
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  categoryChart.setOption(categoryOption)
}

onMounted(async () => {
  try {
    await statisticsStore.fetchTagStats()
    initCharts()
  } catch (error) {
    showToast('获取统计数据失败')
  }
})
</script>

<template>
  <div class="tag-stats">
    <div class="stats-cards">
      <van-card>
        <template #title>标签总数</template>
        <template #desc>
          <span class="highlight">
            {{ tagStats?.total || 0 }}
          </span>
          个标签
        </template>
      </van-card>
      
      <van-card>
        <template #title>本月新增</template>
        <template #desc>
          <span class="highlight">
            {{ tagStats?.monthly_new || 0 }}
          </span>
          个标签
        </template>
      </van-card>
      
      <van-card>
        <template #title>使用最多</template>
        <template #desc>
          <span class="highlight">
            {{ tagStats?.most_used?.name || '-' }}
          </span>
          ({{ tagStats?.most_used?.count || 0 }}次)
        </template>
      </van-card>
    </div>

    <div class="charts">
      <div class="chart-container">
        <div class="chart-title">标签使用频率</div>
        <div ref="wordCloudRef" class="chart" />
      </div>

      <div class="chart-container">
        <div class="chart-title">标签分类分布</div>
        <div ref="categoryChartRef" class="chart" />
      </div>
    </div>

    <div class="recent-tags" v-if="tagStats?.recent.length">
      <div class="list-title">最近使用的标签</div>
      <van-cell-group inset>
        <van-cell 
          v-for="tag in tagStats?.recent"
          :key="tag.id"
          :title="tag.name"
        >
          <template #right-icon>
            <span class="tag-count">{{ tag.count }}次</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <van-empty v-if="!tagStats && !isLoading" description="暂无数据" />
    <van-loading v-if="isLoading" vertical>加载中...</van-loading>
  </div>
</template>

<style lang="scss" scoped>
.tag-stats {
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
    margin-bottom: var(--van-padding-lg);
    
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
    }
  }
  
  .recent-tags {
    .list-title {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: var(--van-padding-sm);
    }
    
    .tag-count {
      color: var(--van-text-color-2);
      font-size: 14px;
    }
  }
}
</style>