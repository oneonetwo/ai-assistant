<template>
  <div class="home-view">
    <div class="header-buttons">
      <!-- Theme toggle button -->
      <div class="theme-button" @click="themeStore.toggleTheme">
        <van-icon 
          :name="themeStore.isDark ? 'bulb-o' : 'bulb-o'" 
          class="theme-icon" 
          size="32"
        />
      </div>
      
      <!-- Settings button -->
      <div class="settings-button" @click="router.push('/settings')">
        <van-icon name="setting-o" class="settings-icon" size="32"/>
      </div>
    </div>

    <div class="content">
      <h1 class="title">AI 智囊</h1>
      
      <div class="module-grid">
        <!-- 对话模块 -->
        <div class="module-card" @click="router.push('/chat')">
          <div class="card-content">
            <van-icon name="chat" class="module-icon"/>
            <h2>AI智能对话</h2>
            <p>与 AI 助手进行自然对话，获取帮助与建议</p>
          </div>
          <div class="card-overlay"></div>
        </div>

        <!-- 知识库模块 -->
        <div class="module-card" @click="router.push('/handbooks')">
          <div class="card-content">
            <van-icon name="notes" class="module-icon"/>
            <h2>知识管理</h2>
            <p>构建和管理你的个人知识库</p>
          </div>
          <div class="card-overlay"></div>
        </div>

        <!-- 学习计划模块 - 更新为包含子模块 -->
        <div class="module-card learning-module"  @click="router.push('/revision')">
          <div class="card-content">
            <van-icon name="label" class="module-icon"/>
            <h2>学习计划</h2>
            <p>制定个性化学习计划，追踪学习进度</p>
            
            <!-- 子模块网格 -->
            <div class="sub-modules">
              <div class="sub-module" @click.stop="router.push('/statistics')">
                <van-icon name="chart-trending-o" class="sub-icon"/>
                <span>学习统计</span>
              </div>
              <div class="sub-module" @click.stop="router.push('/revision/daily-summary')">
                <van-icon name="description" class="sub-icon"/>
                <span>每日摘要</span>
              </div>
              <div class="sub-module" @click.stop="router.push('/revision/settings/notification')">
                <van-icon name="clock-o" class="sub-icon"/>
                <span>提醒设置</span>
              </div>
            </div>
          </div>
          <div class="card-overlay"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Icon } from 'vant'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const themeStore = useThemeStore()
</script>

<style scoped>
.home-view {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
}

.content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #333;
  text-align: center;
}

.title {
  font-size: 3rem;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #42b883, #35495e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 30px rgba(66, 184, 131, 0.2);
  animation: glow 3s ease-in-out infinite alternate;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  padding: 0 2rem;
}

.module-card {
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
}

.module-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04),
    inset 0 0 25px rgba(255, 255, 255, 0.1);
  border-color: rgba(66, 184, 131, 0.4);
  background: rgba(255, 255, 255, 0.15);
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(66, 184, 131, 0.1), rgba(53, 73, 94, 0.1));
  z-index: -1;
  transition: opacity 0.4s ease;
  opacity: 0;
}

.module-card:hover::before {
  opacity: 1;
}

.card-content {
  position: relative;
  z-index: 1;
}

.module-icon {
  font-size: 48px;
  margin-bottom: 1rem;
  color: var(--van-primary-color);
  transition: transform 0.3s ease;
}

.module-card:hover .module-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 0 8px rgba(66, 184, 131, 0.3));
}

h2 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  color: #333;
  transition: color 0.3s ease;
}

p {
  color: #666;
  font-size: 0.9rem;
  transition: color 0.3s ease;
  line-height: 1.5;
}

.header-buttons {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 2;
  display: flex;
  gap: 1rem;
}

.theme-button,
.settings-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  cursor: pointer;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.theme-button:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(66, 184, 131, 0.4);
  box-shadow: 
    0 0 15px rgba(66, 184, 131, 0.3),
    0 0 5px rgba(66, 184, 131, 0.2);
}

.settings-button:hover {
  transform: rotate(90deg);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(66, 184, 131, 0.4);
  box-shadow: 
    0 0 15px rgba(66, 184, 131, 0.3),
    0 0 5px rgba(66, 184, 131, 0.2);
}

.theme-icon,
.settings-icon {
  font-size: 24px;
  color: #333;
  transition: color 0.3s ease;
}

/* Dark theme styles */
:root[data-theme="dark"] {
  .module-card {
    background: rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .module-card:hover {
    background: rgba(0, 0, 0, 0.3);
    border-color: rgba(66, 184, 131, 0.4);
  }

  h2 {
    color: #fff;
  }

  p {
    color: #aaa;
  }

  .theme-button,
  .settings-button {
    background: rgba(0, 0, 0, 0.2);
  }

  .theme-button:hover,
  .settings-button:hover {
    background: rgba(0, 0, 0, 0.3);
  }

  .theme-icon,
  .settings-icon {
    color: #fff;
  }
}

/* Responsive styles */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  
  .module-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 0 1rem;
  }

  .module-card {
    padding: 1.5rem;
  }

  .header-buttons {
    top: 0.5rem;
    right: 0.5rem;
    gap: 0.5rem;
  }

  .theme-button,
  .settings-button {
    width: 40px;
    height: 40px;
  }
}

.learning-module {
  /* 移除原有的点击事件样式 */
  cursor: default;
}

.learning-module:hover {
  transform: translateY(-5px);
}

.sub-modules {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sub-module {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
}

.sub-module:hover {
  background: rgba(66, 184, 131, 0.1);
  transform: translateY(-2px);
}

.sub-icon {
  font-size: 24px;
  margin-bottom: 0.5rem;
  color: var(--van-primary-color);
}

.sub-module span {
  font-size: 0.85rem;
  color: inherit;
}

/* Dark theme additions */
:root[data-theme="dark"] {
  .sub-modules {
    border-top-color: rgba(255, 255, 255, 0.05);
  }

  .sub-module {
    background: rgba(0, 0, 0, 0.2);
  }

  .sub-module:hover {
    background: rgba(66, 184, 131, 0.15);
  }

  .sub-module span {
    color: #fff;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sub-modules {
    gap: 0.25rem;
    margin-top: 1rem;
    padding-top: 0.75rem;
  }

  .sub-module {
    padding: 0.5rem;
  }

  .sub-icon {
    font-size: 20px;
    margin-bottom: 0.25rem;
  }

  .sub-module span {
    font-size: 0.75rem;
  }
}
</style>