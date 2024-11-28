<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import SvgIcon from './SvgIcon.vue'

const router = useRouter()
const themeStore = useThemeStore()

defineProps<{
  showBack?: boolean
  title?: string
}>()
</script>

<template>
  <div class="app-header">
    <van-nav-bar
      :title="title"
      :left-arrow="showBack"
      @click-left="router.back()"
    >
      <template #left>
        <template v-if="!showBack">
          <van-button 
            class="nav-button"
            @click="router.push('/')"
          >
            <template #icon>
              <svg-icon name="home" class="nav-icon" />
            </template>
            首页
          </van-button>
        </template>
      </template>
      
      <template #right>
        <van-space :size="8">
          <van-button
            class="nav-button"
            @click="router.push('/settings')"
          >
            <template #icon>
              <svg-icon name="setting" class="nav-icon" />
            </template>
            设置
          </van-button>
          <van-button 
            class="nav-button theme-button"
            @click="themeStore.toggleTheme"
          >
            <template #icon>
              <svg-icon 
                :name="themeStore.isDark ? 'sun' : 'moon'" 
                class="nav-icon"
              />
            </template>
            {{ themeStore.isDark ? '浅色' : '深色' }}
          </van-button>
        </van-space>
      </template>
    </van-nav-bar>
  </div>
</template>

<style lang="scss" scoped>
.app-header {
  border-bottom: 1px solid var(--van-border-color);
  background: var(--van-background-2);
  backdrop-filter: blur(10px);
  
  :deep {
    .van-nav-bar {
    background: transparent;
    height: 56px;
    line-height: 56px;
    
    &__content {
      height: 56px;
    }
    
    &__title {
      font-size: 18px;
      font-weight: 600;
    }
    
    &__left, &__right {
      font-size: 16px;
    }
  }
  }
  
  .nav-button {
    height: 36px;
    padding: 0 12px;
    color: var(--van-text-color);
    background: transparent;
    transition: all 0.2s ease;
    border: none;
    
    &:hover {
      color: var(--van-primary-color);
      background: rgba(var(--van-primary-color-rgb), 0.1);
    }
    
    .nav-icon {
      width: 20px;
      height: 20px;
      margin-right: 4px;
      vertical-align: -0.125em;
    }
  }
  
  // 移动端样式
  @media (max-width: 768px) {
    :deep{
        .van-nav-bar {
      height: 46px;
      line-height: 46px;
      
      &__content {
        height: 46px;
      }
    }
    }
    
    .nav-button {
      padding: 0 8px;
      height: 32px;
      
      &:not(.theme-button) {
        .van-button__text {
          display: none;
        }
        
        .nav-icon {
          margin-right: 0;
        }
      }
    }
  }
}
    
// 深色模式
:deep {
    .dark {
  .nav-button {
    &:hover {
      background: rgba(var(--van-primary-color-rgb), 0.15);
    }
    }
  }
}
</style> 