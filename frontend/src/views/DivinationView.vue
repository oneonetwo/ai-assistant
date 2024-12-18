<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { showToast } from 'vant'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  }
})

const systemPromptMd = ref(
  `你是一位经验丰富的命理学家，专精于生辰八字、紫微斗数，深谙阴阳五行、天干地支及八卦易经的奥秘。你擅长以通俗易懂的方式解释复杂的命理知识，为用户提供清晰、可靠的命理分析与方向建议。你的目标是帮助用户更好地理解自己、掌握机遇，同时尊重命运的多样性与可塑性。

### **你的职责与分析原则**
1. 用深入浅出的语言解释五行、天干地支、用神等命理概念，确保用户能够理解分析的依据和过程。
2. 避免使用绝对性的语言，不做确定性预言，重点强调个人努力对命运的积极影响。
3. 保护用户隐私，不主动要求敏感信息，仅根据用户提供的数据进行分析。
4. 针对生辰八字，通过结合天干地支、五行、用神喜忌等详细推演命理。
5. 如果用户切换到西方占星、塔罗牌等领域，你需自然过渡，保持专业水准。

### **回答逻辑与核心内容**
1. 从用户提供的出生信息推算四柱（年柱、月柱、日柱、时柱），分析命理结构，包括五行分布、强弱及平衡关系。
2. 根据八字的整体格局推导命主的性格、婚姻、事业、健康、流年运势等多方面的详细信息。
3. 使用大运分析表，按照起运时间详细列出每10年的运势特点，包括年份、天干地支、五行属性及运势关键点。
4. 针对用户的具体问题，提供详细、可操作的建议，语气友好，如与朋友闲谈般自然。

### **回答风格与格式**
- 所有回答应避免生硬的书面化结构，使用朋友般自然、亲切的语气，像聊天一样娓娓道来。
- 不使用“分析”、“结论”、“建议”等标签性语言，而是以故事化、互动化的形式传递信息。
- 即使内容涉及深奥理论，也应配以通俗易懂的解释，让用户感到亲切并易于接受。

### **补充说明**
无论用户的提问如何复杂或细致，都应以温暖和包容的态度接纳。始终以帮助用户找到清晰的方向为目标，为他们提供积极的力量与实际的指导。

### **要求**
1. 一定要严格按照 你的职责与分析原则 和  回答逻辑与核心内容 进行全面分析，不要遗漏任何信息。
`
)

const systemPrompt = computed(() => {
  return renderMarkdown(systemPromptMd.value)
})

const birthday = ref('1992年10月25日21点30分')
const question = ref('我的事业怎么样？')
const result = ref('')
const isLoading = ref(false)

const chatStore = useChatStore()

function renderMarkdown(content: string): string {
  return md.render(content)
}

async function handleSubmit() {
  if (!systemPrompt.value || !birthday.value || !question.value) {
    showToast('请填写完整信息')
    return
  }

  isLoading.value = true
  try {
    const response = await chatStore.sendMessageDivination({
      systemPrompt: systemPromptMd.value,
      content: `农历日期: ${birthday.value}\n问题: ${question.value}`,
      conversationId: '9690fac4-2a04-4ece-87b2-90c7764c73b7',
      onChunk: (message) => {
        result.value = renderMarkdown(message)
      }
    })
  } catch (error) {
    showToast('请求失败,请重试')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="divination">
    <div class="divination-form">
      <van-form @submit="handleSubmit">
        <van-cell-group inset>
          <van-cell>
            <template #default>
              <div class="markdown-body prompt-content" v-html="systemPrompt" />
            </template>
          </van-cell>
          
          <van-field
            v-model="birthday"
            label="生日"
            placeholder="请输入生日(YYYY-MM-DD)"
            :rules="[{ required: true, message: '请输入生日' }]"
          />

          <van-field
            v-model="question"
            label="问题"
            type="textarea"
            placeholder="请输入您的问题"
            :rules="[{ required: true, message: '请输入问题' }]"
            rows="3"
            autosize
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button 
            round 
            block 
            type="primary" 
            native-type="submit"
            :loading="isLoading"
          >
            开始占卜
          </van-button>
        </div>
      </van-form>
    </div>

    <div v-if="result" class="divination-result">
        <div class="result-title">占卜结果</div>
        <div class="markdown-body result-content" v-html="result" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.divination {
  padding: var(--van-padding-md);
  
  .divination-form {
    margin-bottom: var(--van-padding-lg);
  }

  .submit-btn {
    margin: var(--van-padding-lg) var(--van-padding-md);
  }

  :deep {
    .van-cell {
      padding: var(--van-padding-sm);
    }

    .prompt-title,
    .result-title {
      font-size: var(--van-font-size-lg);
      font-weight: bold;
      margin-bottom: var(--van-padding-xs);
    }

    .prompt-content,
    .result-content {
      padding: var(--van-padding-sm);
      background: var(--van-background-2);
      border-radius: var(--van-radius-md);
      text-align: left;
      p {
        margin: var(--van-padding-xs) 0;
        line-height: 1.6;
      }

      h1, h2, h3, h4, h5, h6 {
        margin: var(--van-padding-sm) 0;
        font-weight: bold;
      }

      ul, ol {
        padding-left: var(--van-padding-lg);
        margin: var(--van-padding-xs) 0;
      }

      li {
        margin: var(--van-padding-xs) 0;
      }

      code {
        background: var(--van-background);
        padding: 2px 4px;
        border-radius: var(--van-radius-sm);
      }

      pre {
        background: var(--van-background);
        padding: var(--van-padding-sm);
        border-radius: var(--van-radius-md);
        overflow-x: auto;
      }

      blockquote {
        border-left: 4px solid var(--van-gray-3);
        padding-left: var(--van-padding-sm);
        margin: var(--van-padding-xs) 0;
        color: var(--van-gray-6);
      }
    }
  }
}
.divination-result{
  padding-bottom: 50px;

}
</style>
