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

    <aside 
      class="sidebar" 
      :class="{ 'sidebar-show': showSidebar }"
    >
      <div class="sidebar-header">
        <van-button 
          block 
          type="primary"
          @click="handleNewChat"
        >
          <template #icon>
            <svg-icon name="plus" />
          </template>
          新建会话
        </van-button>
      </div>

      <div class="conversation-list">
        <ConversationList 
          @select="() => { 
            if (isMobile) showSidebar = false 
          }" 
        />
      </div>
    </aside>

    <div class="main-wrapper">
      <AppHeader :title="route.meta.title as string">
        <template #left>
          <van-button
            v-if="isMobile"
            icon="bars"
            @click="showSidebar = true"
          />
        </template>
      </AppHeader>

      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  background: var(--van-background);
  
  .sidebar-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 100;
  }
  
  .sidebar {
    width: 260px;
    display: flex;
    flex-direction: column;
    background: var(--van-background-2);
    border-right: 1px solid var(--van-border-color);
    
    .sidebar-header {
      padding: 12px;
      border-bottom: 1px solid var(--van-border-color);
    }
    
    .conversation-list {
      flex: 1;
      overflow-y: auto;
    }
  }
  
  .main-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  
  .main-content {
    flex: 1;
    overflow-y: auto;
  }
}

// 移动端样式
@media (max-width: 768px) {
  .chat-layout {
    .sidebar {
      position: fixed;
      top: 0;
      bottom: 0;
      left: -260px;
      z-index: 101;
      transition: transform 0.3s ease;
      
      &.sidebar-show {
        transform: translateX(260px);
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import ConversationList from '@/components/chat/ConversationList.vue'
import AppHeader from '@/components/common/AppHeader.vue'
import SvgIcon from '@/components/common/SvgIcon.vue'

const route = useRoute()
const chatStore = useChatStore()

// 控制侧边栏显示
const showSidebar = ref(window.innerWidth > 768)
const isMobile = computed(() => window.innerWidth <= 768)

// 处理新建会话
function handleNewChat() {
  chatStore.createNewConversation()
  if (isMobile.value) {
    showSidebar.value = false
  }
}

// 处理窗口大小变化
function handleResize() {
  showSidebar.value = window.innerWidth > 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script> 