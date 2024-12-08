<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const settingItems = [
  {
    title: '提醒设置',
    icon: 'bell',
    desc: '设置复习提醒时间和方式',
    path: '/revision/settings/notification'
  },
  {
    title: '每日摘要',
    icon: 'description',
    desc: '查看今日学习计划和进度',
    path: '/revision/daily-summary'
  },
  {
    title: '复习历史',
    icon: 'clock',
    desc: '查看历史复习记录和统计',
    path: '/revision/history'
  },
  {
    title: '学习统计',
    icon: 'chart-trending-o',
    desc: '查看学习数据分析',
    path: '/revision/statistics'
  }
]
</script>

<template>
  <div class="revision-settings">
    <van-nav-bar
      title="复习设置"
      left-arrow
      @click-left="$router.back()"
    />
    
    <div class="settings-content">
      <van-cell-group inset>
        <van-cell
          v-for="item in settingItems"
          :key="item.path"
          :title="item.title"
          :label="item.desc"
          is-link
          center
          @click="router.push(item.path)"
        >
          <template #icon>
            <van-icon 
              :name="item.icon" 
              class="setting-icon"
            />
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.revision-settings {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .settings-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
  }
  
  .setting-icon {
    font-size: 24px;
    margin-right: 8px;
    color: var(--van-primary-color);
  }
}
</style> 