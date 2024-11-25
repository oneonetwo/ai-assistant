<template>
  <div class="chat-layout">
    <!-- 移动端遮罩 -->
    <Transition name="fade">
      <div 
        v-if="showSidebar && isMobile" 
        class="sidebar-mask"
        @click="showSidebar = false"
      />
    </Transition>

    <aside class="sidebar" :class="{ show: showSidebar }">
      <div class="sidebar-header">
        <van-button class="new-chat" block @click="handleNewChat">
          <template #icon>
            <svg-icon name="plus" />
          </template>
          新建会话
        </van-button>
      </div>

      <div class="conversation-list">
        <ConversationList @select="() => { showSidebar = isMobile ? false : true }" />
      </div>

      <div class="sidebar-footer">
        <van-button class="theme-toggle" block @click="themeStore.toggleTheme">
          <template #icon>
            <svg-icon :name="themeStore.isDark ? 'sun' : 'moon'" />
          </template>
          {{ themeStore.isDark ? '浅色模式' : '深色模式' }}
        </van-button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style lang="scss" scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  
  .sidebar {
    width: 260px;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--van-border-color);
    background: var(--van-background-2);
    
    .sidebar-header {
      padding: 12px;
      border-bottom: 1px solid var(--van-border-color);
      
      .new-chat {
        --van-button-default-background: var(--van-primary-color);
        --van-button-default-color: #fff;
        font-weight: 500;
      }
    }
    
    .conversation-list {
      flex: 1;
      overflow-y: auto;
    }
    
    .sidebar-footer {
      padding: 12px;
      border-top: 1px solid var(--van-border-color);
      
      .theme-toggle {
        --van-button-default-background: transparent;
        --van-button-default-border-color: transparent;
        justify-content: flex-start;
        font-weight: 500;
      }
    }
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: var(--van-background);
  }
}
</style> 

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useThemeStore } from '@/stores/theme'
import ConversationList from '@/components/chat/ConversationList.vue'
import SvgIcon from '@/components/common/SvgIcon.vue'

const chatStore = useChatStore()
const themeStore = useThemeStore()

// 控制侧边栏显示
const showSidebar = ref(window.innerWidth > 768)
const isMobile = computed(() => window.innerWidth <= 768)

// 处理新建会话
function handleNewChat() {
  chatStore.createNewConversation()
}

// 处理窗口大小变化
function handleResize() {
  if (!isMobile.value) {
    showSidebar.value = true
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script> 