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
  
  const tagList = tags ? tags.split(',').map(t => t.trim()) : []
  
  snippets.value.unshift({
    id: nanoid(),
    code,
    language,
    description,
    tags: tagList,
    createdAt: Date.now()
  })
}
</script> 