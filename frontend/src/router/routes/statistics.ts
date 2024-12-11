/*
 * @Author: yangjingyuan yangjingyuan@pwrd.com
 * @Date: 2024-12-09 09:59:06
 * @LastEditors: yangjingyuan yangjingyuan@pwrd.com
 * @LastEditTime: 2024-12-11 11:08:22
 * @FilePath: \frontend\src\router\routes\statistics.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import type { RouteRecordRaw } from 'vue-router'

export const statisticsRoutes: RouteRecordRaw[] = [
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/statistics/StatisticsView.vue'),
    meta: {
      title: '学习统计',
      requiresAuth: true
    }
  }
] 