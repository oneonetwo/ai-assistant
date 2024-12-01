<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'
import type { Message } from '@/types/chat';
import { ChatClient } from '@/services/api';

const props = defineProps<{
  messages: Pick<Message, 'role' | 'content' | 'id'>[]
  systemPrompt: string
  onClose: () => void
}>()

const analyzing = ref(true)
const analysisResult = ref('')
const currentSection = ref('')

async function startAnalysis() {
  try {
    const chatClient = new ChatClient()
    await chatClient.streamAnalyze(props.messages, props.systemPrompt, {
      onStart: () => {
        analyzing.value = true
      },
      onChunk: (content: string, section: string, fullText: string) => {
        console.log('content.......', content)
        console.log('section.......', section)
        console.log('fullText.......', fullText)    
        analysisResult.value = fullText
        currentSection.value = section
      },
      onEnd: () => {
        analyzing.value = false
      },
      onError: (error: Error) => {
        showToast(error.message)
        analyzing.value = false
      }
    })
  } catch (error) {
    showToast('分析失败')
    analyzing.value = false
  }
}

// 初始化时开始分析
startAnalysis()
</script>

<template>
  <div class="analyze-overlay">
    <div class="analyze-content">
      <div v-if="analyzing" class="analyzing">
        <van-loading type="spinner" />
        <p>正在分析整理中...</p>
        <p class="section">{{ currentSection }}</p>
      </div>
      
      <div v-else class="result">
        <div class="content" v-html="analysisResult"></div>
        
        <div class="actions">
          <van-button 
            block 
            type="primary"
            @click="$router.push({
              name: 'note-create',
              query: {
                title: '对话分析整理',
                content: analysisResult,
              }
            })"
          >
            创建笔记
          </van-button>
          
          <van-button 
            block 
            plain
            @click="onClose"
          >
            取消
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.analyze-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--van-background);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.analyze-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.analyzing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  
  .section {
    margin-top: 12px;
    color: var(--van-gray-6);
  }
}

.result {
  .content {
    margin-bottom: 20px;
    line-height: 1.6;
  }
  
  .actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: sticky;
    bottom: 20px;
  }
}
</style> 