<script setup lang="ts">
import { ref, computed } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { Tag } from '@/types/handbook'

const props = defineProps<{
  modelValue: string[]
  maxTags?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const store = useHandbookStore()
const searchKeyword = ref('')
const newTagName = ref('')

// 过滤标签建议
const tagSuggestions = computed(() => {
  if (!searchKeyword.value) return store.tags
  
  const keyword = searchKeyword.value.toLowerCase()
  return store.tags.filter(tag => 
    tag.name.toLowerCase().includes(keyword) &&
    !props.modelValue.includes(tag.name)
  )
})

// 添加标签
async function handleAddTag(tagName: string) {
  if (props.maxTags && props.modelValue.length >= props.maxTags) {
    showToast(`最多只能选择 ${props.maxTags} 个标签`)
    return
  }

  const newTags = [...props.modelValue]
  if (!newTags.includes(tagName)) {
    newTags.push(tagName)
    emit('update:modelValue', newTags)
  }
}

// 创建新标签
async function handleCreateTag() {
  if (!newTagName.value) return
  
  try {
    await store.createTag(newTagName.value)
    handleAddTag(newTagName.value)
    newTagName.value = ''
  } catch {
    showToast('创建标签失败')
  }
}

// 移除标签
function handleRemoveTag(tagName: string) {
  const newTags = props.modelValue.filter(t => t !== tagName)
  emit('update:modelValue', newTags)
}
</script>

<template>
  <div class="tag-selector">
    <!-- 已选标签 -->
    <div class="selected-tags">
      <van-tag
        v-for="tagName in modelValue"
        :key="tagName"
        closeable
        type="primary"
        @close="handleRemoveTag(tagName)"
      >
        {{ tagName }}
      </van-tag>
    </div>

    <!-- 搜索和创建 -->
    <div class="tag-input">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索标签"
        shape="round"
      >
        <template #right-icon>
          <van-button
            v-if="searchKeyword"
            size="small"
            type="primary"
            @click="handleCreateTag"
          >
            创建
          </van-button>
        </template>
      </van-search>
    </div>

    <!-- 标签建议 -->
    <div class="tag-suggestions">
      <van-tag
        v-for="tag in tagSuggestions"
        :key="tag.id"
        plain
        class="suggestion-tag"
        @click="handleAddTag(tag.name)"
      >
        {{ tag.name }}
      </van-tag>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tag-selector {
  .selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: var(--van-padding-xs);
  }

  .tag-input {
    margin-bottom: var(--van-padding-xs);
    
    :deep(.van-search__content) {
      flex: 1;
    }
  }

  .tag-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .suggestion-tag {
      cursor: pointer;
      
      &:hover {
        opacity: 0.8;
      }
    }
  }
}
</style> 