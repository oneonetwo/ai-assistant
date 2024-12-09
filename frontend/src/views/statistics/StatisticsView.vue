<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Tabbar, TabbarItem } from 'vant'

const router = useRouter()
const activeTab = ref('overview')

const tabs = [
  { name: 'overview', title: '统计概览', icon: 'chart-trending-o' },
  { name: 'study-time', title: '学习时长', icon: 'clock-o' },
  { name: 'mastery', title: '知识掌握', icon: 'flag-o' },
  { name: 'revision', title: '复习计划', icon: 'calendar-o' },
  { name: 'tags', title: '标签统计', icon: 'label-o' }
]

function onTabChange(name: string) {
  activeTab.value = name
  router.push({ name: `Statistics${name.charAt(0).toUpperCase() + name.slice(1)}` })
}
</script>

<template>
  <div class="statistics-view">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <van-tabbar v-model="activeTab" @change="onTabChange">
      <van-tabbar-item 
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :icon="tab.icon"
      >
        {{ tab.title }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style lang="scss" scoped>
.statistics-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
}
</style> 