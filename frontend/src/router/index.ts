import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import ChatView from '@/views/ChatView.vue'
import { useChatStore } from '@/stores/chat'

// 定义路由配置
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'chat',
    component: ChatView,
    meta: {
      title: 'AI 助手'
    }
  },
  {
    path: '/share/:id',
    name: 'share',
    component: () => import('@/views/ShareView.vue'),
    meta: {
      title: '分享对话'
    }
  },
  {
    path: '/snippets',
    name: 'snippets',
    component: () => import('@/views/SnippetsView.vue'),
    meta: {
      title: '代码片段'
    }
  },
  {
    path: '/settings',
    name: 'settings', 
    component: () => import('@/views/SettingsView.vue'),
    meta: {
      title: '设置'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'AI 助手'}`
  
  // 初始化聊天状态
  if (to.name === 'chat') {
    const chatStore = useChatStore()
    try {
      await chatStore.initializeChat()
    } catch (error) {
      console.error('初始化聊天失败:', error)
    }
  }
  
  next()
})

// 错误处理
router.onError((error) => {
  console.error('路由错误:', error)
})

export default router 