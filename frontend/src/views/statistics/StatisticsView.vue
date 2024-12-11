<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useStatisticsStore } from '@/stores/statistics'
import { Tabbar, TabbarItem } from 'vant'
import AppHeader from '@/components/common/AppHeader.vue'
import StudyTimeStats from '../../components/statistics/StudyTimeStats.vue'
import MasteryStats from '../../components/statistics/MasteryStats.vue'
import RevisionStats from '../../components/statistics/RevisionStats.vue'
import TagStats from '../../components/statistics/TagStats.vue'

const statisticsStore = useStatisticsStore()
const activeTab = ref('study-time')

// 创建每个部分的ref用于滚动定位
const studyTimeRef = ref<HTMLElement | null>(null)
const masteryRef = ref<HTMLElement | null>(null)
const revisionRef = ref<HTMLElement | null>(null)
const tagsRef = ref<HTMLElement | null>(null)

// 将ref映射到名称
const sectionRefs = {
  'study-time': studyTimeRef,
  'mastery': masteryRef,
  'revision': revisionRef,
  'tags': tagsRef
}

const tabs = [
  { name: 'study-time', title: '学习时长', icon: 'clock-o' },
  { name: 'mastery', title: '知识掌握', icon: 'flag-o' },
  { name: 'revision', title: '复习计划', icon: 'calendar-o' },
  { name: 'tags', title: '标签统计', icon: 'label-o' }
]

// 处理标签切换和滚动
function onTabChange(name: string) {
  activeTab.value = name
  const targetElement = sectionRefs[name as keyof typeof sectionRefs].value
  if (targetElement) {
    // 添加顶部偏移，避免被导航栏遮挡
    const offset = 60 // 根据实际导航栏高度调整
    const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - offset
    window.scrollTo({
      top: elementPosition,
      behavior: 'smooth'
    })
  }
}

// 监听滚动位置更新激活的标签
function onScroll() {
  const scrollPosition = window.scrollY + window.innerHeight / 3 // 调整触发位置

  for (const [name, ref] of Object.entries(sectionRefs)) {
    if (ref.value) {
      const { top, bottom } = ref.value.getBoundingClientRect()
      const threshold = window.innerHeight / 3
      
      if (top <= threshold && bottom >= threshold) {
        if (activeTab.value !== name) {
          activeTab.value = name
        }
        break
      }
    }
  }
}

// 初始化数据和滚动监听
onMounted(async () => {
  await statisticsStore.initializeStatistics()
  window.addEventListener('scroll', onScroll)
})

// 清理滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <div class="statistics-view">
    <!-- 添加头部导航 -->
    <AppHeader title="学习统计" />
    
    <div class="statistics-content">
      <!-- 学习时长统计 -->
      <section ref="studyTimeRef" class="stats-section">
        <h2>学习时长统计</h2>
        <study-time-stats />
      </section>

      <!-- 知识掌握统计 -->
      <section ref="masteryRef" class="stats-section">
        <h2>知识掌握统计</h2>
        <mastery-stats />
      </section>

      <!-- 复习计划统计 -->
      <section ref="revisionRef" class="stats-section">
        <h2>复习计划统计</h2>
        <revision-stats />
      </section>

      <!-- 标签使用统计 -->
      <section ref="tagsRef" class="stats-section">
        <h2>标签使用统计</h2>
        <tag-stats />
      </section>
    </div>

    <!-- 底部导航栏 -->
    <van-tabbar v-model="activeTab" @change="onTabChange" fixed>
      <van-tabbar-item 
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :icon="tab.icon"
      >
        {{ tab.title }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style lang="scss" scoped>
.statistics-view {
  min-height: 100vh;
  padding-bottom: var(--van-tabbar-height);
  background-color: var(--van-background);
  
  .statistics-content {
    padding: var(--van-padding-md);
    padding-top: 56px; // 为固定头部预留空间
    
    .stats-section {
      margin-bottom: var(--van-padding-xl);
      scroll-margin-top: 60px; // 为固定导航栏预留空间
      background-color: var(--van-background-2);
      border-radius: var(--van-radius-lg);
      padding: var(--van-padding-md);
      
      h2 {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: var(--van-padding-md);
        color: var(--van-text-color);
      }
    }
  }
  
  :deep(.van-tabbar) {
    border-top: 1px solid var(--van-border-color);
    
    .van-tabbar-item {
      color: var(--van-text-color);
      
      &--active {
        color: var(--van-primary-color);
      }
    }
  }
}
</style> 