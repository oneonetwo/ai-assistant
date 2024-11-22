<template>
  <div class="message" :class="{ 'message-ai': message.role === 'assistant' }">
    <div class="message-content">
      <div class="markdown-body" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

interface Props {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: number
    status: string
  }
}

const props = defineProps<Props>()

// 配置 markdown-it
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  highlight: function (str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(str, { 
          language: lang,
          ignoreIllegals: true 
        }).value
        
        return `
          <div class="code-block">
            <div class="code-header">
              <span class="language">${lang}</span>
              <button class="copy-button" onclick="navigator.clipboard.writeText(\`${str.replace(/`/g, '\\`')}\`)">
                复制代码
              </button>
            </div>
            <pre><code class="hljs language-${lang}">${highlighted}</code></pre>
          </div>`
      } catch (__) {
        console.log('highlight error:', __)
      }
    }
    return `<pre><code>${md.utils.escapeHtml(str)}</code></pre>`
  }
})

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!props.message?.content) return ''
  return md.render(props.message.content)
})
</script>

<style lang="scss">

.message {
  padding: 16px;
  
  &-ai {
    background: var(--van-background-2);
  }
  
  &-content {
    max-width: 800px;
    margin: 0 auto;
    
    .markdown-body {
      font-size: 15px;
      line-height: 1.6;
      
      p {
        margin: 8px 0;
      }
      
      pre {
        margin: 16px 0;
      }
    }
  }
}
</style>
