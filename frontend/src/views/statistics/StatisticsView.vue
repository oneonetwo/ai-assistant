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
  background: linear-gradient(135deg, var(--van-background) 0%, rgba(var(--van-primary-color), 0.05) 100%);
  
  .statistics-content {
    padding: var(--van-padding-md);
    padding-top: 60px;
    
    .stats-section {
      margin-bottom: var(--van-padding-xl);
      scroll-margin-top: 60px;
      background: linear-gradient(
        145deg,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0.05) 100%
      );
      border-radius: var(--van-radius-lg);
      padding: var(--van-padding-lg);
      box-shadow: 
        20px 20px 60px rgba(0, 0, 0, 0.1),
        -20px -20px 60px rgba(255, 255, 255, 0.1),
        inset 0 0 0 1px rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      transform: perspective(1000px) translateZ(0);
      transform-style: preserve-3d;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: inherit;
        background: linear-gradient(
          45deg,
          transparent 0%,
          rgba(255, 255, 255, 0.1) 100%
        );
        z-index: -1;
        transition: opacity 0.3s ease;
        opacity: 0;
      }
      
      &:hover {
        transform: perspective(1000px) translateZ(20px) rotateX(2deg) rotateY(2deg);
        box-shadow: 
          30px 30px 80px rgba(0, 0, 0, 0.15),
          -30px -30px 80px rgba(255, 255, 255, 0.15),
          inset 0 0 0 1px rgba(255, 255, 255, 0.15);
          
        &::before {
          opacity: 1;
        }
      }
      
      h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: var(--van-padding-lg);
        color: var(--van-text-color);
        padding-bottom: var(--van-padding-xs);
        position: relative;
        display: inline-block;
        text-shadow: 0 0 10px rgba(var(--van-primary-color), 0.3);
        
        &::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          height: 2px;
          background: linear-gradient(
            90deg,
            var(--van-primary-color) 0%,
            transparent 100%
          );
          box-shadow: 0 0 10px rgba(var(--van-primary-color), 0.5);
        }
      }
    }
  }
  
  :deep {
    .van-tabbar {
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      background: linear-gradient(
        180deg,
        rgba(var(--van-background-2), 0.8) 0%,
        rgba(var(--van-background-2), 0.95) 100%
      );
      box-shadow: 
        0 -10px 20px rgba(0, 0, 0, 0.1),
        0 -4px 6px rgba(0, 0, 0, 0.05);
      
      .van-tabbar-item {
        color: var(--van-gray-6);
        font-size: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        
        &__icon {
          font-size: 20px;
          margin-bottom: 4px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.2));
        }
        
        &--active {
          color: var(--van-primary-color);
          font-weight: 500;
          text-shadow: 0 0 10px rgba(var(--van-primary-color), 0.3);
          
          .van-tabbar-item__icon {
            transform: translateY(-2px) scale(1.1);
            filter: drop-shadow(0 0 4px rgba(var(--van-primary-color), 0.5));
          }
        }
        
        &:active {
          transform: scale(0.95);
        }
      }
    }
  }
}
</style> 