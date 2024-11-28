<script setup lang="ts">
import { ref } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showDialog, showToast } from 'vant'
import type { Tag } from '@/types/handbook'

const store = useHandbookStore()
const searchKeyword = ref('')

// 过滤标签
const filteredTags = computed(() => {
  if (!searchKeyword.value) return store.tags
  
  const keyword = searchKeyword.value.toLowerCase()
  return store.tags.filter(tag => 
    tag.name.toLowerCase().includes(keyword)
  )
})

// 按使用次数排序的热门标签
const popularTags = computed(() => {
  return [...store.tags]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
})

async function handleCreate() {
  try {
    const name = await showDialog({
      title: '创建标签',
      message: '请输入标签名称',
      showCancelButton: true,
      confirmButtonText: '创建'
    })
    
    if (name) {
      await store.createTag(name)
      showToast('创建成功')
    }
  } catch {
    // 用户取消
  }
}

async function handleDelete(tag: Tag) {
  try {
    await showDialog({
      title: '删除标签',
      message: '确定要删除这个标签吗？',
      showCancelButton: true
    })
    
    await store.deleteTag(tag.id)
    showToast('删除成功')
  } catch {
    // 用户取消或删除失败
  }
}
</script>

<template>
  <div class="tag-manager">
    <div class="header">
      <h2>标签管理</h2>
      <van-button 
        type="primary" 
        size="small"
        icon="plus"
        @click="handleCreate"
      >
        新建标签
      </van-button>
    </div>

    <van-search
      v-model="searchKeyword"
      placeholder="搜索标签"
      shape="round"
    />

    <div class="popular-tags" v-if="!searchKeyword">
      <div class="section-title">常用标签</div>
      <div class="tag-cloud">
        <van-tag
          v-for="tag in popularTags"
          :key="tag.id"
          type="primary"
          plain
          size="medium"
          class="tag-item"
        >
          {{ tag.name }} ({{ tag.count }})
        </van-tag>
      </div>
    </div>

    <div class="tag-list">
      <div class="section-title">所有标签</div>
      <van-cell-group>
        <van-swipe-cell
          v-for="tag in filteredTags"
          :key="tag.id"
        >
          <van-cell :title="tag.name">
            <template #right-icon>
              <span class="tag-count">{{ tag.count }}次使用</span>
            </template>
          </van-cell>
          
          <template #right>
            <van-button
              square
              type="danger"
              class="delete-button"
              @click="handleDelete(tag)"
            >
              删除
            </van-button>
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tag-manager {
  padding: var(--van-padding-md);

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--van-padding-md);
    
    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }
  }

  .section-title {
    margin: var(--van-padding-md) 0;
    font-size: 16px;
    font-weight: 500;
    color: var(--van-text-color);
  }

  .popular-tags {
    margin-bottom: var(--van-padding-lg);
    
    .tag-cloud {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
  }

  .tag-count {
    font-size: 14px;
    color: var(--van-text-color-2);
  }

  .delete-button {
    height: 100%;
  }
}
</style> 