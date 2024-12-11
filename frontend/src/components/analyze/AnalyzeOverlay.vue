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
  background: var(--van-background-2);
  border-bottom: 2px solid var(--van-border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .handbook-selector {
    width: 220px;
    :deep {
      .van-field {
        background: transparent;
        border-radius: 8px;
        border: 1px solid var(--van-border-color);
      }
    }
  }

  .actions {
    display: flex;
    gap: 12px;
    align-items: center;

    :deep {
      .van-button {
        border-radius: 8px;
        font-weight: 500;
        
        &.close-button {
          padding: 8px;
          background: var(--van-background-2);
          border: 1px solid var(--van-border-color);
        }
      }
    }
  }
}

.analyze-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--van-background);
  
  // 添加纸张纹理效果
  background-image: linear-gradient(
    rgba(var(--van-gray-1), 0.05) 1px,
    transparent 1px
  );
  background-size: 100% 32px;
}

.analyzing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  
  :deep {
    .van-loading {
      color: var(--van-primary-color);
    }
  }
  
  p {
    margin-top: 16px;
    color: var(--van-text-color-2);
    font-size: 15px;
  }
}

.result {
  max-width: 800px;
  margin: 0 auto;
  
  .content {
    background: var(--van-background-2);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    
    :deep {
      .markdown-body {
        font-size: 15px;
        line-height: 1.8;
        color: var(--van-text-color);
        
        h1, h2, h3 {
          margin-top: 1.5em;
          margin-bottom: 0.8em;
          font-weight: 600;
          color: var(--van-text-color);
        }
        
        h1 {
          font-size: 1.8em;
          padding-bottom: 0.5em;
          border-bottom: 2px solid var(--van-border-color);
        }
        
        h2 {
          font-size: 1.5em;
        }
        
        h3 {
          font-size: 1.2em;
        }
        
        p {
          margin: 1em 0;
        }
        
        pre {
          margin: 16px 0;
          padding: 16px;
          border-radius: 8px;
          background: var(--code-background);
          border: 1px solid var(--van-border-color);
          
          code {
            font-family: var(--van-font-family-code);
            font-size: 14px;
            line-height: 1.6;
          }
        }
        
        ul, ol {
          padding-left: 1.5em;
          margin: 1em 0;
        }
        
        li {
          margin: 0.5em 0;
        }
        
        blockquote {
          margin: 1em 0;
          padding: 0.5em 1em;
          border-left: 4px solid var(--van-primary-color);
          background: var(--van-background);
          color: var(--van-text-color-2);
        }
      }
    }
  }
}

// 暗黑主题特定样式
:root[data-theme="dark"] {
  .analyze-content {
    background-image: linear-gradient(
      rgba(255, 255, 255, 0.03) 1px,
      transparent 1px
    );
  }
  
  .result .content {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  }
}
</style> 