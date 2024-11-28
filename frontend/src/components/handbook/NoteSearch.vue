<script setup lang="ts">
import { ref } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { useRouter } from 'vue-router'
import type { Note } from '@/types/handbook'

const router = useRouter()
const store = useHandbookStore()

// 搜索条件
const keyword = ref('')
const selectedTags = ref<string[]>([])
const selectedPriority = ref<Note['priority'] | ''>('')
const selectedStatus = ref<Note['status'] | ''>('')
const dateRange = ref<[Date | null, Date | null]>([null, null])
const sortBy = ref<'created' | 'updated' | 'priority'>('updated')
const sortOrder = ref<'asc' | 'desc'>('desc')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 搜索结果
const searchResults = ref<Note[]>([])
const total = ref(0)
const isLoading = ref(false)

// 执行搜索
async function handleSearch() {
  try {
    isLoading.value = true
    const response = await store.searchNotes({
      keyword: keyword.value,
      tags: selectedTags.value,
      priority: selectedPriority.value,
      status: selectedStatus.value,
      startDate: dateRange.value[0]?.getTime(),
      endDate: dateRange.value[1]?.getTime(),
      sortBy: sortBy.value,
      sortOrder: sortOrder.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    
    searchResults.value = response.data
    total.value = response.total
  } catch (error) {
    showToast('搜索失败')
  } finally {
    isLoading.value = false
  }
}

// 监听搜索条件变化
watch(
  [keyword, selectedTags, selectedPriority, selectedStatus, dateRange, sortBy, sortOrder],
  () => {
    currentPage.value = 1
    handleSearch()
  }
)

// 处理分页变化
function handlePageChange(page: number) {
  currentPage.value = page
  handleSearch()
}
</script>

<template>
  <div class="note-search">
    <van-search
      v-model="keyword"
      placeholder="搜索笔记"
      shape="round"
    />

    <div class="filters">
      <van-collapse>
        <van-collapse-item title="筛选条件">
          <div class="filter-group">
            <div class="filter-title">标签</div>
            <div class="tag-selector">
              <van-tag
                v-for="tag in store.tags"
                :key="tag.id"
                :type="selectedTags.includes(tag.name) ? 'primary' : 'default'"
                class="tag-item"
                @click="
                  selectedTags.includes(tag.name)
                    ? selectedTags = selectedTags.filter(t => t !== tag.name)
                    : selectedTags.push(tag.name)
                "
              >
                {{ tag.name }}
              </van-tag>
            </div>
          </div>

          <div class="filter-group">
            <div class="filter-title">优先级</div>
            <van-radio-group v-model="selectedPriority" direction="horizontal">
              <van-radio name="">全部</van-radio>
              <van-radio name="low">低</van-radio>
              <van-radio name="medium">中</van-radio>
              <van-radio name="high">高</van-radio>
            </van-radio-group>
          </div>

          <div class="filter-group">
            <div class="filter-title">状态</div>
            <van-radio-group v-model="selectedStatus" direction="horizontal">
              <van-radio name="">全部</van-radio>
              <van-radio name="draft">草稿</van-radio>
              <van-radio name="published">已发布</van-radio>
              <van-radio name="archived">已归档</van-radio>
            </van-radio-group>
          </div>

          <div class="filter-group">
            <div class="filter-title">日期范围</div>
            <van-date-picker
              v-model="dateRange"
              type="range"
              title="选择日期范围"
            />
          </div>
        </van-collapse-item>
      </van-collapse>
    </div>

    <div class="sort-bar">
      <van-dropdown-menu>
        <van-dropdown-item v-model="sortBy" :options="[
          { text: '更新时间', value: 'updated' },
          { text: '创建时间', value: 'created' },
          { text: '优先级', value: 'priority' }
        ]" />
        <van-dropdown-item v-model="sortOrder" :options="[
          { text: '降序', value: 'desc' },
          { text: '升序', value: 'asc' }
        ]" />
      </van-dropdown-menu>
    </div>

    <div class="search-results">
      <van-list
        v-model:loading="isLoading"
        :finished="currentPage * pageSize >= total"
        finished-text="没有更多了"
        @load="handlePageChange(currentPage + 1)"
      >
        <van-cell
          v-for="note in searchResults"
          :key="note.id"
          :title="note.title"
          :label="note.content.slice(0, 50) + (note.content.length > 50 ? '...' : '')"
          is-link
          @click="router.push(`/notes/${note.id}`)"
        >
          <template #right-icon>
            <div class="note-meta">
              <van-tag 
                :type="note.priority === 'high' ? 'danger' : note.priority === 'medium' ? 'warning' : 'success'"
                size="small"
              >
                {{ note.priority }}
              </van-tag>
              <van-tag 
                :type="note.status === 'published' ? 'primary' : 'default'"
                size="small"
              >
                {{ note.status }}
              </van-tag>
            </div>
          </template>
        </van-cell>
      </van-list>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.note-search {
  height: 100vh;
  display: flex;
  flex-direction: column;

  .filters {
    border-bottom: 1px solid var(--van-border-color);
  }

  .filter-group {
    margin-bottom: var(--van-padding-md);

    .filter-title {
      margin-bottom: var(--van-padding-xs);
      font-weight: 500;
    }

    .tag-selector {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      .tag-item {
        cursor: pointer;
      }
    }
  }

  .sort-bar {
    margin-bottom: var(--van-padding-md);
  }

  .search-results {
    flex-grow: 1;
    overflow-y: auto;
  }
}
</style>