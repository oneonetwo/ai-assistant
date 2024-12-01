<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const analyzing = ref(true)
const analysisResult = ref('')
const currentSection = ref('')

onMounted(async () => {
  console.log('systemPrompt.......', route.params)
  const messages = JSON.parse(route.params.messages as string)
  const systemPrompt = route.params.systemPrompt as string
  await startAnalysis(messages, systemPrompt)
})

async function startAnalysis(messages: Message[], systemPrompt: string) {
  try {

    return
    const chatClient = new ChatClient()
    await chatClient.streamAnalyze(messages, {
      systemPrompt,
      onStart: () => {
        analyzing.value = true
      },
      onChunk: (content: string, section: string, fullText: string) => {
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

function handleCreateNote() {
  router.push({
    name: 'note-create',
    query: {
      title: '对话分析整理',
      content: analysisResult.value,
      messageIds: JSON.stringify(Array.from(selectedMessages.value)),
      handbookId: route.query.handbookId as string
    }
  })
}
</script>

<template>
  <div class="analyze-view">
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
          @click="handleCreateNote"
        >
          创建笔记
        </van-button>
        
        <van-button 
          block 
          plain
          @click="router.back()"
        >
          取消
        </van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  padding: 20px;
  
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
