<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import type { Message } from '@/types/chat';
import { ChatClient } from '@/services/api';
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { useHandbookStore } from '@/stores/handbook'
import Selector from '@/components/common/Selector.vue'
import { useRouter } from 'vue-router'
import { useNoteEditorStore } from '@/stores/noteEditor'

const props = defineProps<{
  messages: Pick<Message, 'role' | 'content' | 'id'>[]
  systemPrompt: string
  onClose: () => void
}>()

const analyzing = ref(true)
const analysisResult = ref('')
const currentSection = ref('')
const selectedHandbook = ref<number>()

const handbookStore = useHandbookStore()
const router = useRouter()
const noteEditorStore = useNoteEditorStore()

// 获取手册列表
onMounted(async () => {
  await handbookStore.fetchHandbooks()
})

// 转换手册数据为 Selector 需要的格式
const handbookOptions = computed(() => {
  return handbookStore.handbooks.map(handbook => ({
    text: handbook.name,
    value: handbook.id
  }))
})

// 判断是否可以创建笔记
const canCreate = computed(() => {
  return !analyzing.value && selectedHandbook.value !== undefined && analysisResult.value
})

// 初始化 markdown-it
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  }
})

// 添加计算属性用于渲染 markdown
const renderedContent = computed(() => {
  return md.render(analysisResult.value)
})

async function startAnalysis() {
  try {
    const chatClient = new ChatClient()
    await chatClient.streamAnalyze(props.messages, props.systemPrompt, {
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

// 初始化时开始分析
startAnalysis()

// 添加 handleCreateNote 方法
function handleCreateNote() {
  // 设置草稿数据
  noteEditorStore.setDraft({
    title: analysisResult.value.match(/标题[:：]\s*([^\n]+)/)?.[1] || '',
    content: analysisResult.value,
    messageIds: props.messages.map(message => message.id)
  })

  // 跳转到创建页面
  router.push({
    name: 'note-create',
    query: {
      handbook: selectedHandbook.value
    }
  })
}
</script>

<template>
  <div class="analyze-overlay">
    <div class="header">
      <div class="handbook-selector">
        <Selector
          v-model="selectedHandbook"
          :options="handbookOptions"
          placeholder="选择手册"
        />
      </div>
      <div class="actions">
        <van-button 
          type="primary"
          :disabled="!canCreate"
          @click="handleCreateNote"
        >
          创建笔记
        </van-button>
        <van-button 
          icon="cross"
          class="close-button"
          @click="onClose"
        />
      </div>
    </div>

    <div class="analyze-content">
      <div v-if="analyzing" class="analyzing">
        <van-loading type="spinner" />
        <p>正在分析整理中...</p>
      </div>
      
      <div class="result">
        <div class="content markdown-body" v-html="renderedContent"></div>
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--van-border-color);

  .handbook-selector {
    width: 200px;
  }

  .actions {
    display: flex;
    gap: 8px;
    align-items: center;

    .van-button {
      &.close-button {
        padding: 8px;
      }
    }
  }
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
    
    :deep(.markdown-body) {
      font-size: 14px;
      line-height: 1.6;
      
      pre {
        margin: 12px 0;
        padding: 12px;
        border-radius: 4px;
        background: var(--code-background);
        overflow-x: auto;
        
        code {
          font-family: var(--van-font-family-code);
          font-size: 13px;
        }
      }
    }
  }
  
  .actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: sticky;
    bottom: 20px;
  }
}

.footer {
  padding: 16px 20px;
  border-top: 1px solid var(--van-border-color);
  background: var(--van-background);
}
</style> 