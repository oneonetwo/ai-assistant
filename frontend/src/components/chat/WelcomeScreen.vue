<template>
  <div class="welcome-screen">
    <div class="welcome-content">
      <h1>AI 助手</h1>
      <p>选择以下功能开始对话，或直接输入问题</p>
      
      <div class="feature-tags">
        <div 
          v-for="tag in featureTags" 
          :key="tag.id" 
          class="feature-tag" 
          @click="handleTagClick(tag)"
        >
          <svg-icon :name="tag.icon" />
          <span>{{ tag.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

const featureTags = [
  { id: 1, icon: 'image', label: '直接开始对话', prompt: '你好！' },
  { id: 2, icon: 'chart', label: '分析数据', prompt: '请帮我分析以下数据:' },
  { id: 3, icon: 'doc', label: '总结文本', prompt: '请帮我总结以下文本:' },
  { id: 4, icon: 'bulb', label: '构思', prompt: '请帮我构思一个' },
  { id: 5, icon: 'edit', label: '帮我写', prompt: '请帮我写一篇' },
  { id: 6, icon: 'calculator', label: '给我做算', prompt: '请帮我计算' },
  { id: 7, icon: 'analyze', label: '分析图片', prompt: '请帮我分析这张图片:' },
  { id: 8, icon: 'code', label: '代码', prompt: '请帮我编写代码:' }
]

const emit = defineEmits<{
  (e: 'select', tag: typeof featureTags[0]): void
}>()

async function handleTagClick(tag: typeof featureTags[0]) {
  try {
    const currentConversation = chatStore.currentConversation
    
    // 只有在没有当前会话时才创建新会话
    if (!currentConversation) {
      await chatStore.createNewConversation()
    }
    
    // 发送选择事件
    emit('select', tag)
  } catch (error) {
    console.error('处理标签点击失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.welcome-screen {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  
  .welcome-content {
    text-align: center;
    max-width: 600px;
    
    h1 {
      font-size: 24px;
      margin-bottom: 12px;
    }
    
    p {
      color: var(--van-gray-6);
      margin-bottom: 24px;
    }
  }
  
  .feature-tags {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
    
    .feature-tag {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      border-radius: 8px;
      background: var(--van-background-2);
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: var(--van-background-3);
      }
      
      .svg-icon {
        width: 20px;
        height: 20px;
      }
    }
  }
}
</style> 