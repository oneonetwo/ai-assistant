<script setup lang="ts">
import { useRouter } from 'vue-router'
import SvgIcon from '@/components/common/SvgIcon.vue'
import { useWindowSize } from '@vueuse/core'
import { computed } from 'vue';

const router = useRouter()

const { width } = useWindowSize()
const isMobile = computed(() => width.value <= 768)

const features = [
  {
    title: '知识手册',
    description: '笔记管理，知识整理，标签系统',
    icon: 'book',
    route: '/handbooks'
  },
  {
    title: 'AI 助手',
    description: '智能对话，解答问题，代码生成',
    icon: 'chat',
    route: '/chat'
  },
  {
    title: '复习助手',
    description: '执行计划，科学复习',
    icon: 'book',
    route: '/revision'
  }
]
</script>

<template>
  <div class="home-view">
    <header class="header" :class="{ 'header--mobile': isMobile }">
      <h1>AI 智囊</h1>
      <p>你的 知识管理工具 & 智能助手 & 复习助手</p>
    </header>

    <main class="features" :class="{ 'features--mobile': isMobile }">
      <div
        v-for="feature in features"
        :key="feature.title"
        class="feature-card"
        :class="{ 'feature-card--mobile': isMobile }"
        @click="router.push(feature.route)"
      >
        <div class="icon">
          <svg-icon :name="feature.icon" />
        </div>
        <div class="content">
          <h2>{{ feature.title }}</h2>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </main>

    <footer class="footer">
      <van-button
        icon="setting-o"
        :size="isMobile ? 'normal' : 'large'"
        @click="router.push('/settings')"
      >
        设置
      </van-button>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.home-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: var(--van-padding-md);
  max-width: 1200px;
  margin: 0 auto;
  box-sizing: border-box;
  
  .header {
    text-align: center;
    margin: 48px 0;
    
    h1 {
      font-size: clamp(24px, 5vw, 32px);
      font-weight: 600;
      margin-bottom: 12px;
    }
    
    p {
      color: var(--van-text-color-2);
      font-size: clamp(14px, 3vw, 16px);
    }

    &--mobile {
      margin: 24px 0;
    }
  }
  
  .features {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: clamp(16px, 3vw, 24px);
    width: 100%;
    padding: clamp(16px, 3vw, 24px);
    
    &--mobile {
      grid-template-columns: 1fr;
      padding: 16px 0;
    }
    
    .feature-card {
      background: var(--van-background-2);
      border-radius: var(--van-radius-lg);
      padding: clamp(16px, 3vw, 24px);
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: flex-start;
      gap: 16px;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      &--mobile {
        padding: 16px;
      }
      
      .icon {
        flex-shrink: 0;
        width: clamp(40px, 6vw, 48px);
        height: clamp(40px, 6vw, 48px);
        
        .svg-icon {
          width: 100%;
          height: 100%;
          color: var(--van-primary-color);
        }
      }
      
      .content {
        flex: 1;
        
        h2 {
          font-size: clamp(18px, 4vw, 20px);
          font-weight: 600;
          margin-bottom: 8px;
        }
        
        p {
          color: var(--van-text-color-2);
          line-height: 1.5;
          font-size: clamp(14px, 3vw, 16px);
        }
      }
    }
  }
  
  .footer {
    text-align: center;
    padding: clamp(16px, 3vw, 24px) 0;
  }
}

// 媒体查询优化
@media (max-width: 768px) {
  .home-view {
    padding: var(--van-padding-sm);
  }
}

// 深色模式优化
@media (prefers-color-scheme: dark) {
  .feature-card {
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
  }
}
</style> 