<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { NoteStatistics } from '@/types/history'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LineChart,
  CanvasRenderer
])

const props = defineProps<{
  statistics: NoteStatistics
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    updateChart()
  }
})

watch(() => props.statistics, updateChart, { deep: true })

function updateChart() {
  if (!chart) return

  const dates = props.statistics.revision_dates.map(date => 
    new Date(date).toLocaleDateString()
  )

  const option = {
    title: {
      text: '复习趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '复习次数',
        type: 'line',
        data: dates.map(() => 1),
        smooth: true
      }
    ]
  }

  chart.setOption(option)
}

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<template>
  <div ref="chartRef" class="statistics-chart"></div>
</template>

<style lang="scss" scoped>
.statistics-chart {
  width: 100%;
  height: 300px;
}
</style> 