<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { showToast } from 'vant'
import type { EChartsOption } from 'echarts'

const statisticsStore = useStatisticsStore()
const { revisionStats, isLoading } = storeToRefs(statisticsStore)

const trendChartRef = ref<HTMLElement>()
const completionChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()

// 初始化图表
function initCharts() {
  if (!revisionStats.value) return
  
  // 复习计划趋势图
  const trendChart = echarts.init(trendChartRef.value!)
  const trendOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['计划复习', '实际完成']
    },
    xAxis: {
      type: 'category',
      data: revisionStats.value.trend.map(item => item.date),
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '知识点数量'
    },
    series: [
      {
        name: '计划复习',
        type: 'bar',
        data: revisionStats.value.trend.map(item => item.planned),
        itemStyle: { color: '#4f46e5' }
      },
      {
        name: '实际完成',
        type: 'bar',
        data: revisionStats.value.trend.map(item => item.completed),
        itemStyle: { color: '#42b883' }
      }
    ]
  }
  trendChart.setOption(trendOption)

  // 完成率环形图
  const completionChart = echarts.init(completionChartRef.value!)
  const completionRate = revisionStats.value.completed / revisionStats.value.planned
  const completionOption: EChartsOption = {
    series: [{
      type: 'gauge',
      startAngle: 90,
      endAngle: -270,
      pointer: { show: false },
      progress: {
        show: true,
        overlap: false,
        roundCap: true,
        clip: false,
        itemStyle: { color: '#42b883' }
      },
      axisLine: {
        lineStyle: { width: 20 }
      },
      splitLine: { show: false },
      axisTick: { show: false },
      axisLabel: { show: false },
      detail: {
        valueAnimation: true,
        formatter: '{value}%',
        fontSize: 24,
        offsetCenter: [0, 0]
      },
      data: [{
        value: (completionRate * 100).toFixed(1),
        name: '完成率'
      }]
    }]
  }
  completionChart.setOption(completionOption)

  // 分类统计图
  const categoryChart = echarts.init(categoryChartRef.value!)
  const categoryOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['计划复习', '已完成']
    },
    xAxis: {
      type: 'value',
      name: '知识点数量'
    },
    yAxis: {
      type: 'category',
      data: revisionStats.value.categories.map(item => item.name)
    },
    series: [
      {
        name: '计划复习',
        type: 'bar',
        data: revisionStats.value.categories.map(item => item.planned),
        itemStyle: { color: '#4f46e5' }
      },
      {
        name: '已完成',
        type: 'bar',
        data: revisionStats.value.categories.map(item => item.completed),
        itemStyle: { color: '#42b883' }
      }
    ]
  }
  categoryChart.setOption(categoryOption)
}

onMounted(async () => {
  try {
    await statisticsStore.fetchRevisionStats()
    initCharts()
  } catch (error) {
    showToast('获取统计数据失败')
  }
})
</script>

<template>
  <div class="revision-stats">
    <div class="stats-cards">
      <van-card>
        <template #title>计划复习</template>
        <template #desc>
          <span class="highlight">
            {{ revisionStats?.planned || 0 }}
          </span>
          个知识点
        </template>
      </van-card>
      
      <van-card>
        <template #title>已完成</template>
        <template #desc>
          <span class="highlight">
            {{ revisionStats?.completed || 0 }}
          </span>
          个知识点
        </template>
      </van-card>
      
      <van-card>
        <template #title>完成率</template>
        <template #desc>
          <span class="highlight">
            {{ ((revisionStats?.completed || 0) / (revisionStats?.planned || 1) * 100).toFixed(1) }}
          </span>
          %
        </template>
      </van-card>
    </div>

    <div class="charts">
      <div class="chart-container">
        <div class="chart-title">复习计划趋势</div>
        <div ref="trendChartRef" class="chart" />
      </div>

      <div class="chart-container">
        <div class="chart-title">计划完成率</div>
        <div ref="completionChartRef" class="chart" />
      </div>

      <div class="chart-container">
        <div class="chart-title">分类统计</div>
        <div ref="categoryChartRef" class="chart" />
      </div>
    </div>

    <div class="revision-list" v-if="revisionStats?.upcoming.length">
      <div class="list-title">待复习项目</div>
      <van-cell-group inset>
        <van-cell 
          v-for="item in revisionStats?.upcoming"
          :key="item.id"
          :title="item.title"
          :label="item.category"
        >
          <template #right-icon>
            <span class="due-date">{{ item.due_date }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <van-empty v-if="!revisionStats && !isLoading" description="暂无数据" />
    <van-loading v-if="isLoading" vertical>加载中...</van-loading>
  </div>
</template>

<style lang="scss" scoped>
.revision-stats {
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--van-padding-sm);
    margin-bottom: var(--van-padding-lg);
    
    :deep {
      .van-card{
      background: var(--van-background-2);
      border-radius: var(--van-radius-md);
      
      &__title {
        font-size: 14px;
        color: var(--van-text-color-2);
      }
      
      .highlight {
        font-size: 20px;
        font-weight: 600;
        color: var(--van-primary-color);
      }
    }}
  }
  
  .charts {
    .chart-container {
      margin-bottom: var(--van-padding-lg);
      
      .chart-title {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: var(--van-padding-sm);
        color: var(--van-text-color);
      }
      
      .chart {
        height: 300px;
        background: var(--van-background-2);
        border-radius: var(--van-radius-md);
        padding: var(--van-padding-sm);
      }
    }
  }
  
  .revision-list {
    .list-title {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: var(--van-padding-sm);
      color: var(--van-text-color);
    }
    
    .due-date {
      font-size: 14px;
      color: var(--van-danger-color);
    }
  }
}
</style>