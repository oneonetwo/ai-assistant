<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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
  if (!searchKeyword.value) return
  
  try {
    await store.createTag(searchKeyword.value)
    handleAddTag(searchKeyword.value)
    searchKeyword.value = ''
  } catch {
    showToast('创建标签失败')
  }
}

// 移除标签
function handleRemoveTag(tagName: string) {
  const newTags = props.modelValue.filter(t => t !== tagName)
  emit('update:modelValue', newTags)
}

// Replace random color with cycling color
let colorIndex = 0
function getNextColor(): number {
  colorIndex = (colorIndex % 5) + 1
  return colorIndex
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
        :class="['custom-tag', `color-${getNextColor()}`]"
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
            v-if="searchKeyword && tagSuggestions.length === 0"
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
        :class="['suggestion-tag', 'custom-tag', `color-${getNextColor()}`]"
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

  .custom-tag {
    border-radius: 16px !important;
    padding: 4px 10px !important;
    margin: 4px !important;
    border: none !important;
    
    &.color-1 {
      background-color: #00B4DB !important;
      color: #ffffff !important;
    }
    
    &.color-2 {
      background-color: #9BE36D !important;
      color: #2C5E1A !important;
    }
    
    &.color-3 {
      background-color: #A78BFA !important;
      color: #ffffff !important;
    }
    
    &.color-4 {
      background-color: #FF8C82 !important;
      color: #ffffff !important;
    }
    
    &.color-5 {
      background-color: #14B8A6 !important;
      color: #ffffff !important;
    }

    &.van-tag--plain {
      background-color: transparent !important;
      
      &.color-1 {
        border: 1px solid #00B4DB !important;
        color: #00B4DB !important;
        :root[data-theme="dark"] & {
          color: #ffffff !important;
        }
      }
      
      &.color-2 {
        border: 1px solid #9BE36D !important;
        color: #2C5E1A !important;
        :root[data-theme="dark"] & {
          color: #ffffff !important;
        }
      }
      
      &.color-3 {
        border: 1px solid #A78BFA !important;
        color: #A78BFA !important;
        :root[data-theme="dark"] & {
          color: #ffffff !important;
        }
      }
      
      &.color-4 {
        border: 1px solid #FF8C82 !important;
        color: #FF8C82 !important;
        :root[data-theme="dark"] & {
          color: #ffffff !important;
        }
      }
      
      &.color-5 {
        border: 1px solid #14B8A6 !important;
        color: #14B8A6 !important;
        :root[data-theme="dark"] & {
          color: #ffffff !important;
        }
      }
    }
  }
}
</style> 