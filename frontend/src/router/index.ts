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
        path: 'notes/:id/detail',
        name: 'note-detail',
        component: () => import('@/views/handbook/NoteDetailView.vue'),
        meta: {
          title: '笔记详情'
        }
      },
      {
        path: 'notes/:noteId/history',
        name: 'note-history',
        component: () => import('@/views/revision/RevisionHistoryView.vue'),
        meta: {
          title: '复习历史',
          requiresAuth: true
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
  // 复习任务相关路由
  {
    path: '/revision',
    name: 'revision', 
    component: () => import('@/views/revision/RevisionView.vue'),
    meta: {
      title: '复习计划'
    },
    children: [
      {
        path: '',
        name: 'revision-plans', 
        component: () => import('@/views/revision/PlanListView.vue'),
        meta: {
          title: '复习计划'
        }
      },
      {
        path: 'plans/new',
        name: 'revision-plan-new',
        component: () => import('@/views/revision/PlanEditorView.vue'),
        meta: {
          title: '新建计划'
        }
      },
      {
        path: 'plans/:id',
        name: 'revision-plan-detail',
        component: () => import('@/views/revision/PlanDetailView.vue'),
        meta: {
          title: '计划详情'
        }
      },
      {
        path: 'tasks',
        name: 'revision-tasks',
        component: () => import('@/views/revision/TaskListView.vue'),
        meta: {
          title: '复习任务'
        }
      },
      {
        path: 'quick-review',
        name: 'revision-quick-review',
        component: () => import('@/views/revision/QuickReviewView.vue'),
        meta: {
          title: '快速复习'
        }
      },
      {
        path: 'task-review',
        name: 'revision-task-review',
        component: () => import('@/views/revision/TaskReviewView.vue'),
        meta: {
          title: '任务复习'
        }
      },
      {
        path: 'settings',
        name: 'revision-settings',
        component: () => import('@/views/revision/RevisionSettingsView.vue'),
        meta: {
          title: '复习设置'
        }
      },
      {
        path: 'settings/notification',
        name: 'notification-settings',
        component: () => import('@/views/revision/NotificationSettingsView.vue'),
        meta: {
          title: '提醒设置'
        }
      },
      {
        path: 'daily-summary',
        name: 'daily-summary',
        component: () => import('@/views/revision/DailySummaryView.vue'),
        meta: {
          title: '每日摘要'
        }
      },
      {
        path: 'history',
        name: 'revision-history',
        component: () => import('@/views/revision/RevisionHistoryView.vue'),
        meta: {
          title: '复习历史'
        }
      },
      {
        path: 'statistics',
        name: 'learning-statistics',
        component: () => import('@/views/revision/LearningStatsView.vue'),
        meta: {
          title: '学习统计'
        }
      }
    ]
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: {
      title: '��置'
    }
  },
  {
    path: '/analyze',
    name: 'analyze',
    component: () => import('@/views/analyze/AnalyzeView.vue'),
    meta: {
      title: '分析整理'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '页面不存在'
    }
  },
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