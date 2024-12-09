import type { RouteRecordRaw } from 'vue-router'

export const statisticsRoutes: RouteRecordRaw[] = [
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/statistics/StatisticsView.vue'),
    meta: {
      title: '学习统计',
      requiresAuth: true
    },
    children: [
      {
        path: '',
        name: 'StatisticsOverview',
        component: () => import('@/views/statistics/StatisticsOverview.vue'),
        meta: {
          title: '统计概览'
        }
      },
      {
        path: 'study-time',
        name: 'StudyTimeStats',
        component: () => import('@/views/statistics/StudyTimeStats.vue'),
        meta: {
          title: '学习时长统计'
        }
      },
      {
        path: 'mastery',
        name: 'MasteryStats',
        component: () => import('@/views/statistics/MasteryStats.vue'),
        meta: {
          title: '知识点掌握统计'
        }
      },
      {
        path: 'revision',
        name: 'RevisionStats',
        component: () => import('@/views/statistics/RevisionStats.vue'),
        meta: {
          title: '复习计划统计'
        }
      },
      {
        path: 'tags',
        name: 'TagStats',
        component: () => import('@/views/statistics/TagStats.vue'),
        meta: {
          title: '标签使用统计'
        }
      }
    ]
  }
] 