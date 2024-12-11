<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { storeToRefs } from 'pinia'
import * as echarts from 'echarts'
import { showToast } from 'vant'
import type { EChartsOption } from 'echarts'

const statisticsStore = useStatisticsStore()
const { studyTimeStats, isLoading } = storeToRefs(statisticsStore)

const weeklyChartRef = ref<HTMLElement>()
const peakPeriodsChartRef = ref<HTMLElement>()
const selectedDays = ref(30)

const daysOptions = [
  { text: '最近7天', value: 7 },
  { text: '最近30天', value: 30 },
  { text: '最近90天', value: 90 }
]

// 初始化图表
async function initCharts() {
  if (!studyTimeStats.value) return
  
  // 周趋势图表
  const weeklyChart = echarts.init(weeklyChartRef.value!)
  const weeklyOption: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c} 小时'
    },
    xAxis: {
      type: 'category',
      data: studyTimeStats.value.weekly_trend.map(item => item.date),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '学习时长(小时)'
    },
    series: [{
      data: studyTimeStats.value.weekly_trend.map(item => item.hours),
      type: 'line',
      smooth: true,
      areaStyle: {}
    }]
  }
  weeklyChart.setOption(weeklyOption)

  // 高峰时段图表
  const peakPeriodsChart = echarts.init(peakPeriodsChartRef.value!)
  const peakPeriodsOption: EChartsOption = {
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: studyTimeStats.value.peak_periods.map(item => ({
        name: item.period,
        value: item.hours
      }))
    }]
  }
  peakPeriodsChart.setOption(peakPeriodsOption)
}

// 处理时间范围变化
async function handleDaysChange(days: number) {
  selectedDays.value = days
  try {
    await statisticsStore.fetchStudyTimeStats({ days: days })
    initCharts()
  } catch (error) {
    showToast('获取数据失败')
  }
}

onMounted(async () => {
  try {
    await statisticsStore.fetchStudyTimeStats({ days: selectedDays.value }) // 使用days参数
    initCharts()
  } catch (error) {
    showToast('获取数据失败')
  }
})
</script>

<template>
  <div class="study-time-stats">
    <div class="filter-bar">
      <van-dropdown-menu>
        <van-dropdown-item
          v-model="selectedDays"
          :options="daysOptions"
          @change="handleDaysChange"
        />
      </van-dropdown-menu>
    </div>

    <div class="stats-cards">
      <van-card>
        <template #title>总学习时长</template>
        <template #num>
          <span class="highlight">
            {{ studyTimeStats?.total_hours || 0 }}
          </span>
          小时
        </template>
      </van-card>

      <van-card>
        <template #title>日均学习时长</template>
        <template #num>
          <span class="highlight">
            {{ studyTimeStats?.daily_average || 0 }}
          </span>
          小时
        </template>
      </van-card>
    </div>

    <div class="charts">
      <div class="chart-container">
        <div class="chart-title">学习时长趋势</div>
        <div ref="weeklyChartRef" class="chart" />
      </div>

      <div class="chart-container">
        <div class="chart-title">学习高峰时段</div>
        <div ref="peakPeriodsChartRef" class="chart" />
      </div>
    </div>

    <van-empty v-if="!studyTimeStats && !isLoading" description="暂无数据" />
    <van-loading v-if="isLoading" vertical>加载中...</van-loading>
  </div>
</template>

<style lang="scss" scoped>
.study-time-stats {
  padding: var(--van-padding-md);
  
  .filter-bar {
    margin-bottom: var(--van-padding-md);
  }
  
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
    }
  }
}
</style> 