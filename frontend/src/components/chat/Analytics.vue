<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useChart } from '@/composables/useChart'

const chatStore = useChatStore()

// 计算统计数据
const statistics = computed(() => {
  const stats = {
    totalMessages: 0,
    userMessages: 0,
    assistantMessages: 0,
    averageResponseTime: 0,
    messagesByHour: new Array(24).fill(0),
    commonWords: new Map<string, number>()
  }

  let lastUserMessageTime = 0
  let totalResponseTime = 0
  let responseCount = 0

  chatStore.conversations.forEach(conv => {
    conv.messages.forEach(msg => {
      stats.totalMessages++
      
      if (msg.role === 'user') {
        stats.userMessages++
        lastUserMessageTime = msg.timestamp
      } else {
        stats.assistantMessages++
        if (lastUserMessageTime) {
          totalResponseTime += msg.timestamp - lastUserMessageTime
          responseCount++
        }
      }

      // 统计消息时间分布
      const hour = new Date(msg.timestamp).getHours()
      stats.messagesByHour[hour]++

      // 统计常用词
      msg.content.split(/\s+/).forEach(word => {
        if (word.length > 1) {
          stats.commonWords.set(
            word,
            (stats.commonWords.get(word) || 0) + 1
          )
        }
      })
    })
  })

  stats.averageResponseTime = responseCount
    ? totalResponseTime / responseCount / 1000 // 转换为秒
    : 0

  return stats
})

// 使用 echarts 绘制图表
const { chartRef: timeChartRef } = useChart({
  option: computed(() => ({
    title: {
      text: '消息时间分布'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}时`)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: statistics.value.messagesByHour,
      type: 'bar'
    }]
  }))
})

const { chartRef: wordCloudRef } = useChart({
  option: computed(() => ({
    title: {
      text: '常用词云'
    },
    series: [{
      type: 'wordCloud',
      data: Array.from(statistics.value.commonWords.entries())
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 100)
    }]
  }))
})
</script>

<template>
  <div class="analytics">
    <div class="stats-cards">
      <van-card title="总消息数">
        <template #num>
          {{ statistics.totalMessages }}
        </template>
      </van-card>
      
      <van-card title="平均响应时间">
        <template #num>
          {{ statistics.averageResponseTime.toFixed(2) }}s
        </template>
      </van-card>
      
      <van-card title="对话比例">
        <template #num>
          {{ (statistics.assistantMessages / statistics.userMessages).toFixed(2) }}
        </template>
      </van-card>
    </div>

    <div class="charts">
      <div ref="timeChartRef" class="chart" />
      <div ref="wordCloudRef" class="chart" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.analytics {
  padding: var(--van-padding-md);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--van-padding-sm);
  margin-bottom: var(--van-padding-md);
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--van-padding-md);
  
  .chart {
    height: 300px;
    background: var(--van-background-2);
    border-radius: var(--van-radius-md);
  }
}
</style> 