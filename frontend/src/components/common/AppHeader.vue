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
          <!-- <div class="settings-button" @click="router.push('/settings')">
            <van-icon name="setting-o" class="settings-icon" size="24"/>
          </div> -->
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
  
  .settings-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    cursor: pointer;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
      0 4px 6px -1px rgba(0, 0, 0, 0.1),
      0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

  .settings-button:hover {
    transform: rotate(90deg);
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(66, 184, 131, 0.4);
    box-shadow: 
      0 0 15px rgba(66, 184, 131, 0.3),
      0 0 5px rgba(66, 184, 131, 0.2);
  }

  .settings-icon {
    font-size: 24px;
    color: #333;
    transition: color 0.3s ease;
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