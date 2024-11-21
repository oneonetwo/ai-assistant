<script setup lang="ts">
import { ref } from 'vue'

interface PromptTemplate {
  id: string
  title: string
  content: string
  tags: string[]
}

const templates = ref<PromptTemplate[]>([
  {
    id: '1',
    title: '代码审查',
    content: '请帮我审查以下代码，指出潜在的问题和改进建议：\n\n```\n{code}\n```',
    tags: ['编程', '代码']
  },
  {
    id: '2',
    title: '翻译助手',
    content: '请将以下内容翻译成{target_language}：\n\n{text}',
    tags: ['翻译', '语言']
  },
  {
    id: '3',
    title: '文章总结',
    content: '请用简洁的语言总结以下文章的主要内容：\n\n{article}',
    tags: ['写作', '总结']
  }
])

const searchKeyword = ref('')
const selectedTags = ref<string[]>([])

const filteredTemplates = computed(() => {
  return templates.value.filter(template => {
    const matchKeyword = !searchKeyword.value || 
      template.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      template.content.toLowerCase().includes(searchKeyword.value.toLowerCase())
    
    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.some(tag => template.tags.includes(tag))
    
    return matchKeyword && matchTags
  })
})

const allTags = computed(() => {
  const tags = new Set<string>()
  templates.value.forEach(template => {
    template.tags.forEach(tag => tags.add(tag))
  })
  return Array.from(tags)
})

const emit = defineEmits<{
  (e: 'select', content: string): void
}>()

function handleSelect(template: PromptTemplate) {
  emit('select', template.content)
}
</script>

<template>
  <div class="prompt-templates">
    <div class="search-bar">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索模板"
        shape="round"
      />
    </div>
    
    <div class="tags-filter">
      <van-checkbox-group v-model="selectedTags">
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
      </van-checkbox-group>
    </div>
    
    <div class="templates-list">
      <van-cell-group>
        <van-cell
          v-for="template in filteredTemplates"
          :key="template.id"
          :title="template.title"
          is-link
          @click="handleSelect(template)"
        >
          <template #label>
            <MessagePreview :content="template.content" />
          </template>
          
          <template #extra>
            <div class="template-tags">
              <van-tag
                v-for="tag in template.tags"
                :key="tag"
                type="primary"
                plain
                size="small"
              >
                {{ tag }}
              </van-tag>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.prompt-templates {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 