<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { nanoid } from 'nanoid'
import { showToast } from 'vant'

interface CodeSnippet {
  id: string
  code: string
  language: string
  description: string
  tags: string[]
  createdAt: number
}

const snippets = useLocalStorage<CodeSnippet[]>('code-snippets', [])
const searchKeyword = ref('')
const selectedTags = ref<string[]>([])

// 获取所有标签
const allTags = computed(() => {
  const tags = new Set<string>()
  snippets.value.forEach(snippet => {
    snippet.tags.forEach(tag => tags.add(tag))
  })
  return Array.from(tags)
})

// 过滤代码片段
const filteredSnippets = computed(() => {
  return snippets.value.filter(snippet => {
    const matchKeyword = !searchKeyword.value || 
      snippet.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      snippet.code.toLowerCase().includes(searchKeyword.value.toLowerCase())
    
    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.some(tag => snippet.tags.includes(tag))
    
    return matchKeyword && matchTags
  })
})

// 添加代码片段
function addSnippet(code: string, language: string) {
  const description = window.prompt('请输入代码描述：')
  if (!description) return
  
  const tags = window.prompt('请输入标签（用逗号分隔）：')
  if (!tags) return
  
  const tagList = tags.split(',').map(t => t.trim())
  
  snippets.value.unshift({
    id: nanoid(),
    code,
    language,
    description,
    tags: tagList,
    createdAt: Date.now()
  })
  
  showToast('代码片段已收藏')
}

// 删除代码片段
function deleteSnippet(id: string) {
  snippets.value = snippets.value.filter(s => s.id !== id)
  showToast('代码片段已删除')
}

// 复制代码片段
async function copySnippet(code: string) {
  try {
    await navigator.clipboard.writeText(code)
    showToast('代码已复制')
  } catch (error) {
    showToast('复制失败')
  }
}

defineExpose({
  addSnippet
})
</script>

<template>
  <div class="code-snippets">
    <div class="snippets-header">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索代码片段"
        shape="round"
      />
      
      <div class="tags-filter">
        <van-tag
          v-for="tag in allTags"
          :key="tag"
          :text="tag"
          @click="toggleTag(tag)"
          :class="{ active: selectedTags.includes(tag) }"
        />
      </div>
    </div>
    <div class="snippets-list">
      <div class="snippet-item" v-for="snippet in filteredSnippets" :key="snippet.id">
        <div class="snippet-icon">
          <svg-icon name="code" />
        </div>
        <div class="snippet-content">
          <div class="snippet-title">{{ snippet.description }}</div>
          <div class="snippet-language">{{ snippet.language }}</div>
        </div>
        <div class="snippet-actions">
          <van-button
            size="small"
            type="primary"
            @click="copySnippet(snippet.code)"
          >
            复制
          </van-button>
          <van-button
            size="small"
            type="danger"
            @click="deleteSnippet(snippet.id)"
          >
            删除
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.code-snippets {
  padding: 16px;
  background: var(--van-background-2);
  border-radius: 4px;
  
  .snippets-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    
    .tags-filter {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .van-tag {
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        background: var(--van-background-3);
        color: var(--van-text-color-2);
        
        &.active {
          background: var(--van-primary-color);
          color: var(--van-white);
        }
      }
    }
  }
  
  .snippets-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .snippet-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 12px;
      background: var(--van-background-3);
      border-radius: 4px;
      
      .snippet-icon {
        color: var(--van-gray-6);
      }
      
      .snippet-content {
        flex: 1;
        min-width: 0;
        
        .snippet-title {
          font-size: 14px;
          color: var(--van-text-color-2);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .snippet-language {
          font-size: 12px;
          color: var(--van-gray-5);
        }
      }
      
      .snippet-actions {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .van-button {
          padding: 4px 8px;
          border-radius: 4px;
        }
      }
    }
  }
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  
  &.show {
    transform: translateX(0);
  }
}

.sidebar-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 99;
}
</style> 