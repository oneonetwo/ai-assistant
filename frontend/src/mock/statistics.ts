/*
 * @Author: yangjingyuan yangjingyuan@pwrd.com
 * @Date: 2024-12-11 10:43:24
 * @LastEditors: yangjingyuan yangjingyuan@pwrd.com
 * @LastEditTime: 2024-12-11 11:16:32
 * @FilePath: \frontend\src\mock\statistics.ts
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */

import dayjs from 'dayjs'
import { random } from 'lodash-es'

// 生成指定范围内的随机浮点数
function randomFloat(min: number, max: number, decimals = 1): number {
  return Number((Math.random() * (max - min) + min).toFixed(decimals))
}

// 生成过去N天的日期数组
function generateDates(days: number) {
  return Array.from({ length: days }, (_, i) => {
    return dayjs().subtract(days - i - 1, 'day').format('YYYY-MM-DD')
  })
}

// 生成学习时长统计数据
export function generateStudyTimeStats(days = 30) {
  const dates = generateDates(days)
  
  // 生成每日学习时长，工作日4-8小时，周末2-4小时
  const weeklyTrend = dates.map(date => {
    const dayOfWeek = dayjs(date).day()
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
    const hours = isWeekend 
      ? randomFloat(2, 4)
      : randomFloat(4, 8)
    return { date, hours }
  })

  // 生成高峰时段数据，确保总和为当日总学习时长
  const generatePeakPeriods = () => {
    const periods = [
      { period: '早晨 (6:00-9:00)', hours: randomFloat(30, 50) },
      { period: '上午 (9:00-12:00)', hours: randomFloat(60, 90) },
      { period: '下午 (12:00-18:00)', hours: randomFloat(100, 140) },
      { period: '晚上 (18:00-24:00)', hours: randomFloat(70, 100) }
    ]
    return periods
  }

  // 生成月度目标和完成情况
  const monthlyGoals = {
    target_hours: random(120, 160),
    completed_hours: random(100, 140),
    completion_rate: 0,
    daily_goals_met: random(15, 25)
  }
  monthlyGoals.completion_rate = Number((monthlyGoals.completed_hours / monthlyGoals.target_hours).toFixed(2))

  return {
    total_hours: Number(weeklyTrend.reduce((sum, day) => sum + day.hours, 0).toFixed(1)),
    daily_average: Number((weeklyTrend.reduce((sum, day) => sum + day.hours, 0) / days).toFixed(1)),
    weekly_trend: weeklyTrend,
    peak_periods: generatePeakPeriods(),
    monthly_goals: monthlyGoals,
    focus_sessions: {
      total: random(40, 60),
      completed: random(30, 50),
      average_duration: randomFloat(25, 45),
      success_rate: randomFloat(0.7, 0.9, 2)
    },
    learning_streaks: {
      current: random(5, 15),
      longest: random(15, 30),
      total_days: random(50, 80)
    }
  }
}

// 生成知识掌握统计数据
export function generateMasteryStats() {
  const totalPoints = random(200, 300)
  const mastered = random(50, 100)
  const learning = random(80, 120)
  const struggling = totalPoints - mastered - learning

  // 生成知识点掌握进度详情
  const generateProgressDetails = () => {
    const topics = [
      'JavaScript基础', 'ES6+特性', 'TypeScript', 'Vue.js', 'React', 
      'Node.js', 'HTTP协议', 'CSS布局', '前端工程化', '性能优化',
      '设计模式', '数据结构', '算法基础', 'Git版本控制', '数据库基础'
    ]
    
    return topics.map(topic => ({
      topic,
      mastery_level: random(1, 5),
      progress: randomFloat(0, 1, 2),
      last_reviewed: dayjs().subtract(random(1, 30), 'day').format('YYYY-MM-DD'),
      strength: random(1, 100),
      review_count: random(5, 30)
    }))
  }

  return {
    total_points: totalPoints,
    mastered,
    learning,
    struggling,
    mastery_rate: Number((mastered / totalPoints).toFixed(2)),
    category_distribution: {
      '编程基础': random(30, 50),
      '前端开发': random(40, 60),
      '后端开发': random(35, 55),
      '数据库': random(25, 40),
      '系统设计': random(20, 35),
      '算法': random(30, 45)
    },
    progress_details: generateProgressDetails(),
    learning_velocity: {
      daily_new_points: random(3, 8),
      weekly_mastered: random(15, 25),
      retention_rate: randomFloat(0.7, 0.9, 2)
    },
    review_efficiency: {
      average_time: random(5, 15),
      success_rate: randomFloat(0.6, 0.9, 2),
      optimal_interval: random(3, 7)
    }
  }
}

// 生成复习计划统计数据
export function generateRevisionStats(): RevisionStats {
  return {
    planned: 120, // 计划复习的知识点总数
    completed: 85, // 已完成复习的知识点数
    trend: [
      // 最近7天的复习趋势
      { date: '2024-03-01', planned: 15, completed: 12 },
      { date: '2024-03-02', planned: 18, completed: 15 },
      { date: '2024-03-03', planned: 20, completed: 16 },
      { date: '2024-03-04', planned: 16, completed: 14 },
      { date: '2024-03-05', planned: 22, completed: 18 },
      { date: '2024-03-06', planned: 14, completed: 12 },
      { date: '2024-03-07', planned: 15, completed: 13 }
    ],
    upcoming: [
      // 即将需要复习的知识点
      {
        id: 1,
        title: 'Vue 组件生命周期',
        category: '前端开发',
        due_date: '今天'
      },
      {
        id: 2,
        title: 'TypeScript 类型系统',
        category: '编程语言',
        due_date: '明天'
      },
      {
        id: 3,
        title: 'React Hooks 使用',
        category: '前端开发',
        due_date: '后天'
      },
      {
        id: 4,
        title: 'CSS Grid 布局',
        category: '前端开发',
        due_date: '3天后'
      },
      {
        id: 5,
        title: 'Node.js 事件循环',
        category: '后端开发',
        due_date: '4天后'
      }
    ],
    categories: [
      // 按分类统计的复习情况
      { name: '前端开发', planned: 45, completed: 32 },
      { name: '后端开发', planned: 30, completed: 22 },
      { name: '编程语言', planned: 25, completed: 18 },
      { name: '数据库', planned: 20, completed: 13 }
    ],
    completion_rate: {
      // 按时间段的完成率
      daily: 85,
      weekly: 78,
      monthly: 72
    }
  }
}

// 更新 RevisionStats 接口
interface RevisionStats {
  planned: number
  completed: number
  trend: Array<{
    date: string
    planned: number
    completed: number
  }>
  upcoming: Array<{
    id: number
    title: string
    category: string
    due_date: string
  }>
  categories: Array<{
    name: string
    planned: number
    completed: number
  }>
  completion_rate: {
    daily: number
    weekly: number
    monthly: number
  }
}

// 生成标签统计数据
export function generateTagStats() {
  const technologies = [
    { name: 'JavaScript', color: '#f7df1e', category: '前端技术' },
    { name: 'TypeScript', color: '#3178c6', category: '前端技术' },
    { name: 'Vue', color: '#42b883', category: '前端技术' },
    { name: 'React', color: '#61dafb', category: '前端技术' },
    { name: 'Angular', color: '#dd1b16', category: '前端技术' },
    { name: 'Node.js', color: '#339933', category: '后端技术' },
    { name: 'Python', color: '#3776ab', category: '后端技术' },
    { name: 'Java', color: '#007396', category: '后端技术' },
    { name: 'Go', color: '#00add8', category: '后端技术' },
    { name: 'SQL', color: '#e48e00', category: '数据库' },
    { name: 'MongoDB', color: '#47a248', category: '数据库' },
    { name: 'Redis', color: '#dc382d', category: '数据库' },
    { name: 'Git', color: '#f05032', category: '开发工具' },
    { name: 'Docker', color: '#2496ed', category: '开发工具' },
    { name: 'Kubernetes', color: '#326ce5', category: '开发工具' }
  ]

  const tags = technologies.map(tag => ({
    ...tag,
    id: random(1000, 9999),
    count: random(10, 100),
    last_used: dayjs().subtract(random(1, 30), 'day').format('YYYY-MM-DD'),
    related_tags: technologies
      .filter(t => t.name !== tag.name)
      .slice(0, random(2, 5))
      .map(t => t.name),
    usage_trend: Array.from({ length: 30 }, () => random(0, 5))
  }))

  // 生成标签使用历史
  const generateTagHistory = () => {
    return Array.from({ length: 50 }, (_, i) => ({
      id: i + 1,
      tag_name: technologies[random(0, technologies.length - 1)].name,
      used_at: dayjs().subtract(random(1, 30), 'day').format('YYYY-MM-DD HH:mm:ss'),
      context: ['学习笔记', '项目开发', '问题解决', '知识整理'][random(0, 3)],
      associated_content: `内容 ${i + 1}`
    }))
  }

  return {
    total: tags.length,
    monthly_new: random(2, 5),
    most_used: tags.reduce((max, tag) => tag.count > (max?.count || 0) ? tag : max, null),
    tags,
    categories: [
      { name: '前端技术', count: 45, color: '#42b883' },
      { name: '后端技术', count: 35, color: '#4f46e5' },
      { name: '数据库', count: 20, color: '#e48e00' },
      { name: '开发工具', count: 25, color: '#f05032' }
    ],
    recent: tags.slice(0, 5).map(tag => ({
      id: tag.id,
      name: tag.name,
      count: random(5, 15),
      last_used: dayjs().subtract(random(1, 7), 'day').format('YYYY-MM-DD')
    })),
    tag_history: generateTagHistory(),
    usage_statistics: {
      total_usage: random(500, 1000),
      unique_combinations: random(50, 100),
      most_common_pairs: [
        { tags: ['JavaScript', 'TypeScript'], count: random(20, 40) },
        { tags: ['Vue', 'TypeScript'], count: random(15, 35) },
        { tags: ['Node.js', 'Express'], count: random(10, 30) }
      ],
      average_tags_per_item: randomFloat(2, 4, 1)
    }
  }
}

// 生成总体统计数据
export function generateOverallStats() {
  const studyTime = generateStudyTimeStats(7)
  const mastery = generateMasteryStats()
  const revision = generateRevisionStats()
  const tags = generateTagStats()

  return {
    studyTime,
    mastery,
    revision,
    tags,
    summary: {
      total_study_days: random(50, 90),
      total_study_hours: random(200, 400),
      knowledge_points: random(300, 500),
      completion_rate: randomFloat(0.7, 0.9, 2),
      learning_efficiency: randomFloat(0.6, 0.8, 2)
    },
    achievements: {
      total: random(20, 30),
      completed: random(10, 20),
      recent: [
        { name: '学习达人', date: dayjs().subtract(2, 'day').format('YYYY-MM-DD') },
        { name: '知识探索者', date: dayjs().subtract(5, 'day').format('YYYY-MM-DD') },
        { name: '坚持不懈', date: dayjs().subtract(8, 'day').format('YYYY-MM-DD') }
      ]
    }
  }
}

export const statisticsMock = {
  generateStudyTimeStats,
  generateMasteryStats,
  generateRevisionStats,
  generateTagStats,
  generateOverallStats
}
