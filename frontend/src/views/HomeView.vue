<script setup lang="ts">
import { useRouter } from 'vue-router'
import SvgIcon from '@/components/common/SvgIcon.vue'

const router = useRouter()

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
    description: '系统复习，完全掌握',
    icon: 'book',
    route: '/review'
  }
]
</script>

<template>
  <div class="home-view">
    <header class="header">
      <h1>AI 智囊</h1>
      <p>你的 知识管理工具 & 智能助手 & 复习助手</p>
    </header>

    <main class="features">
      <div
        v-for="feature in features"
        :key="feature.title"
        class="feature-card"
        @click="router.push(feature.route)"
      >
        <div class="icon">
          <svg-icon :name="feature.icon" />
        </div>
        <h2>{{ feature.title }}</h2>
        <p>{{ feature.description }}</p>
      </div>
    </main>

    <footer class="footer">
      <van-button
        icon="setting-o"
        @click="router.push('/settings')"
      >
        设置
      </van-button>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.home-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: var(--van-padding-md);
  
  .header {
    text-align: center;
    margin: 48px 0;
    
    h1 {
      font-size: 32px;
      font-weight: 600;
      margin-bottom: 12px;
    }
    
    p {
      color: var(--van-text-color-2);
    }
  }
  
  .features {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    max-width: 960px;
    margin: 0 auto;
    padding: 24px;
    
    .feature-card {
      background: var(--van-background-2);
      border-radius: var(--van-radius-lg);
      padding: 24px;
      cursor: pointer;
      transition: transform 0.2s;
      
      &:hover {
        transform: translateY(-4px);
      }
      
      .icon {
        width: 48px;
        height: 48px;
        margin-bottom: 16px;
        
        .svg-icon {
          width: 100%;
          height: 100%;
          color: var(--van-primary-color);
        }
      }
      
      h2 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
      }
      
      p {
        color: var(--van-text-color-2);
        line-height: 1.5;
      }
    }
  }
  
  .footer {
    text-align: center;
    padding: 24px 0;
  }
}
</style> 