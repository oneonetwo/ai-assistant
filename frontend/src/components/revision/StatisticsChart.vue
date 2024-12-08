<script setup lang="ts">
import { computed } from 'vue';
import type { NoteStatistics } from '@/stores/types';
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, PieChart, BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import VChart from "vue-echarts";

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent
]);

const props = defineProps<{
  statistics: NoteStatistics;
}>();

// 复习趋势数据
const trendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: ['复习次数', '复习时长(分钟)', '质量评分']
  },
  xAxis: {
    type: 'category',
    data: props.statistics.revision_trends.map(item => item.date)
  },
  yAxis: [
    {
      type: 'value',
      name: '次数/分钟',
    },
    {
      type: 'value',
      name: '评分',
      max: 100,
      min: 0
    }
  ],
  series: [
    {
      name: '复习次数',
      type: 'bar',
      data: props.statistics.revision_trends.map(item => item.count)
    },
    {
      name: '复习时长(分钟)',
      type: 'line',
      data: props.statistics.revision_trends.map(item => item.duration)
    },
    {
      name: '质量评分',
      type: 'line',
      yAxisIndex: 1,
      data: props.statistics.revision_trends.map(item => item.quality)
    }
  ]
}));

// 掌握程度分布
const masteryOption = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      type: 'pie',
      radius: '50%',
      data: [
        { value: props.statistics.mastery_levels.low, name: '待加强' },
        { value: props.statistics.mastery_levels.medium, name: '良好' },
        { value: props.statistics.mastery_levels.high, name: '熟练' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}));
</script>

<template>
  <div class="statistics-charts">
    <div class="chart-container">
      <h3>复习趋势</h3>
      <v-chart class="chart" :option="trendOption" autoresize />
    </div>
    
    <div class="chart-container">
      <h3>掌握程度分布</h3>
      <v-chart class="chart" :option="masteryOption" autoresize />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.statistics-charts {
  .chart-container {
    margin-bottom: 20px;
    
    h3 {
      margin-bottom: 12px;
      font-size: 16px;
      color: var(--van-text-color);
    }
    
    .chart {
      height: 300px;
      width: 100%;
    }
  }
}
</style> 