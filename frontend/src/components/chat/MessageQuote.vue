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
          :type="selectedTags.includes(tag) ? 'primary' : 'default'"
          class="filter-tag"
          @click="
            selectedTags.includes(tag)
              ? selectedTags = selectedTags.filter(t => t !== tag)
              : selectedTags.push(tag)
          "
        >
          {{ tag }}
        </van-tag>
      </div>
    </div>
    
    <div class="snippets-list">
      <template v-if="filteredSnippets.length">
        <div
          v-for="snippet in filteredSnippets"
          :key="snippet.id"
          class="snippet-item"
        >
          <div class="snippet-header">
            <h3 class="snippet-title">{{ snippet.description }}</h3>
            <div class="snippet-actions">
              <van-button
                size="mini"
                icon="copy-o"
                @click="copySnippet(snippet.code)"
              />
              <van-button
                size="mini"
                icon="delete-o"
                @click="deleteSnippet(snippet.id)"
              />
            </div>
          </div>
          
          <pre class="snippet-code"><code :class="snippet.language">{{ snippet.code }}</code></pre>
          
          <div class="snippet-footer">
            <div class="snippet-tags">
              <van-tag
                v-for="tag in snippet.tags"
                :key="tag"
                type="primary"
                plain
                size="small"
              >
                {{ tag }}
              </van-tag>
            </div>
            <span class="snippet-time">
              {{ new Date(snippet.createdAt).toLocaleString() }}
            </span>
          </div>
        </div>
      </template>
      
      <van-empty
        v-else
        description="暂无代码片段"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.code-snippets {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.snippets-header {
  padding: var(--van-padding-sm);
  border-bottom: 1px solid var(--van-border-color);
}

.tags-filter {
  margin-top: var(--van-padding-xs);
  overflow-x: auto;
  white-space: nowrap;
  
  &::-webkit-scrollbar {
    display: none;
  }
}

.filter-tag {
  margin-right: var(--van-padding-xs);
  cursor: pointer;
}

.snippets-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--van-padding-sm);
}

.snippet-item {
  margin-bottom: var(--van-padding-md);
  padding: var(--van-padding-sm);
  background: var(--van-background-2);
  border-radius: var(--van-radius-md);
}

.snippet-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--van-padding-xs);
  
  .snippet-title {
    color: var(--van-text-color);
    font-weight: 500;
  }
  
  .snippet-actions {
    display: flex;
    align-items: center;
  }
}

.snippet-code {
  margin-bottom: var(--van-padding-xs);
}

.snippet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--van-padding-xs);
  
  .snippet-tags {
    display: flex;
    align-items: center;
  }
  
  .snippet-time {
    color: var(--van-text-color-2);
    font-size: 12px;
  }
}
</style> 