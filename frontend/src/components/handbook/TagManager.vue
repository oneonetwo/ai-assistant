<script setup lang="ts">
import { ref, computed } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showDialog, showToast } from 'vant'
import type { Tag } from '@/types/handbook'

const store = useHandbookStore()
const searchKeyword = ref('')
const selectedTags = ref<number[]>([])
const isSelectionMode = ref(false)

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
    .sort((a, b) => (b as any).count - (a as any).count)
    .slice(0, 10)
})

// 切换选择模式
function toggleSelectionMode() {
  isSelectionMode.value = !isSelectionMode.value
  if (!isSelectionMode.value) {
    selectedTags.value = []
  }
}

// 创建标签
async function handleCreate() {
  try {
    const name = await showDialog({
      title: '创建标签',
      message: '请输入标签名称',
      showCancelButton: true,
      confirmButtonText: '创建'
    })
    
    if (!name) return
    
    await store.createTag(name)
    showToast('创建成功')
  } catch {
    showToast('创建失败')
  }
}

// 编辑标签
async function handleEdit(tag: Tag) {
  try {
    const newName = await showDialog({
      title: '编辑标签',
      message: '请输入新的标签名称',
      defaultValue: tag.name,
      showCancelButton: true,
      confirmButtonText: '保存'
    })
    
    if (!newName || newName === tag.name) return
    
    await store.updateTag(tag.id, newName)
    showToast('更新成功')
  } catch {
    showToast('更新失败')
  }
}

// 删除标签
async function handleDelete(tag: Tag) {
  try {
    await showDialog({
      title: '确认删除',
      message: '删除标签将同时从所有笔记中移除该标签，确定要删除吗？',
      showCancelButton: true
    })
    
    await store.deleteTag(tag.id)
    showToast('删除成功')
  } catch (error) {
    if (error) {
      showToast('删除失败')
    }
  }
}

// 合并标签
async function handleMerge() {
  try {
    // 选择源标签
    const sourceTag = await showDialog({
      title: '选择要合并的源标签',
      message: '这个标签将被合并到目标标签中',
      showCancelButton: true,
      confirmButtonText: '下一步'
    })
    
    if (!sourceTag) return
    
    // 选择目标标签
    const targetTag = await showDialog({
      title: '选择合并的目标标签',
      message: '源标签将被合并到这个标签中',
      showCancelButton: true,
      confirmButtonText: '合并'
    })
    
    if (!targetTag) return
    
    await store.mergeTags(sourceTag.id, targetTag.id)
    showToast('合并成功')
  } catch {
    showToast('合并失败')
  }
}

// 批量删除
async function handleBatchDelete() {
  if (!selectedTags.value.length) {
    showToast('请先选择标签')
    return
  }

  try {
    await showDialog({
      title: '确认删除',
      message: `确定要删除选中的 ${selectedTags.value.length} 个标签吗？`,
      showCancelButton: true
    })
    
    // 依次删除选中的标签
    await Promise.all(
      selectedTags.value.map(tagId => store.deleteTag(tagId))
    )
    
    showToast('删除成功')
    selectedTags.value = []
    isSelectionMode.value = false
  } catch (error) {
    if (error) {
      showToast('删除失败')
    }
  }
}

// 批量合并
async function handleBatchMerge() {
  if (selectedTags.value.length < 2) {
    showToast('请至少选择两个标签')
    return
  }

  try {
    // 选择目标标签
    const targetTagId = await showDialog({
      title: '选择合并的目标标签',
      message: '其他标签将被合并到这个标签中',
      showCancelButton: true,
      confirmButtonText: '合并'
    })
    
    if (!targetTagId) return
    
    // 依次合并到目标标签
    const sourceTagIds = selectedTags.value.filter(id => id !== targetTagId)
    await Promise.all(
      sourceTagIds.map(sourceId => store.mergeTags(sourceId, targetTagId))
    )
    
    showToast('合并成功')
    selectedTags.value = []
    isSelectionMode.value = false
  } catch {
    showToast('合并失败')
  }
}
</script>

<template>
  <div class="tag-manager">
    <!-- 搜索和操作栏 -->
    <div class="header">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索标签"
        shape="round"
      />
      
      <van-button 
        type="primary" 
        icon="plus"
        @click="handleCreate"
      >
        新建标签
      </van-button>
    </div>

    <!-- 热门标签 -->
    <div class="popular-tags">
      <div class="section-title">热门标签</div>
      <div class="tag-cloud">
        <van-tag
          v-for="tag in popularTags"
          :key="tag.id"
          type="primary"
          plain
        >
          {{ tag.name }}
          <span class="tag-count">({{ (tag as any).count }})</span>
        </van-tag>
      </div>
    </div>

    <!-- 标签列表 -->
    <div class="tag-list">
      <div class="section-title">所有标签</div>
      <van-empty v-if="!filteredTags.length" description="暂无标签" />
      <van-cell-group v-else>
        <van-swipe-cell
          v-for="tag in filteredTags"
          :key="tag.id"
        >
          <van-cell :title="tag.name">
            <template #right-icon>
              <van-button 
                size="small"
                icon="edit"
                @click.stop="handleEdit(tag)"
              />
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

    <!-- 批量操作 -->
    <van-action-bar>
      <van-action-bar-button
        type="primary"
        icon="cluster-o"
        text="合并标签"
        @click="handleMerge"
      />
    </van-action-bar>
  </div>
</template>

<style lang="scss" scoped>
.tag-manager {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: var(--van-padding-md);

  .header {
    display: flex;
    align-items: center;
    gap: var(--van-padding-md);
    margin-bottom: var(--van-padding-md);
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
    font-size: 12px;
    color: var(--van-gray-6);
    margin-left: 4px;
  }

  .tag-list {
    flex: 1;
    overflow-y: auto;
  }

  .delete-button {
    height: 100%;
  }

  .toolbar {
    display: flex;
    gap: var(--van-padding-xs);
    margin-bottom: var(--van-padding-md);
  }

  // 选择模式下的样式
  :deep(.van-checkbox) {
    margin-right: var(--van-padding-xs);
  }
}
</style> 