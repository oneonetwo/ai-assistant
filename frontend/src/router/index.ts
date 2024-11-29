import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import { useChatStore } from '@/stores/chat'

// 定义路由配置
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'AI 智囊'
    }
  },
  // AI 助手相关路由
  {
    path: '/chat',
    component: () => import('@/components/layout/ChatLayout.vue'),
    children: [
      {
        path: '',
        name: 'chat',
        component: () => import('@/views/ChatView.vue'),
        meta: {
          title: 'AI 对话'
        }
      },
      {
        path: 'share/:id',
        name: 'chat-share',
        component: () => import('@/views/ShareView.vue'),
        meta: {
          title: '分享对话'
        }
      },
      {
        path: 'snippets',
        name: 'snippets',
        component: () => import('@/views/SnippetsView.vue'),
        meta: {
          title: '代码片段'
        }
      }
    ]
  },
  // 知识手册相关路由
  {
    path: '/handbooks',
    component: () => import('@/components/layout/HandbookLayout.vue'),
    children: [
      {
        path: '',
        name: 'handbooks',
        component: () => import('@/views/handbook/HandbookListView.vue'),
        meta: {
          title: '知识手册'
        }
      },
      {
        path: ':id',
        name: 'handbook-detail',
        component: () => import('@/views/handbook/HandbookDetailView.vue'),
        meta: {
          title: '笔记列表'
        }
      },
      {
        path: 'notes/new',
        name: 'note-create',
        component: () => import('@/views/handbook/NoteEditorView.vue'),
        meta: {
          title: '新建笔记'
        }
      },
      {
        path: 'notes/:id',
        name: 'note-edit',
        component: () => import('@/views/handbook/NoteEditorView.vue'),
        meta: {
          title: '编辑笔记'
        }
      },
      {
        path: 'tags',
        name: 'tags',
        component: () => import('@/views/handbook/TagManagerView.vue'),
        meta: {
          title: '标签管理'
        }
      }
    ]
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