<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { showDialog, showToast } from 'vant'
import type { Note } from '@/types/handbook'

const route = useRoute()
const store = useHandbookStore()
const handbookId = route.params.id as string

// 筛选条件
const searchKeyword = ref('')
const selectedTags = ref<string[]>([])
const selectedPriority = ref<Note['priority'] | ''>('')
const selectedStatus = ref<Note['status'] | ''>('')
const priorityOptions = ref<{ text: string; value: Note['priority'] }[]>([
  { text: '全部优先级', value: '' },
  { text: '高', value: 'high' },
  { text: '中', value: 'medium' },
  { text: '低', value: 'low' }
])

const statusOptions = ref<{ text: string; value: Note['status'] }[]>([
  { text: '全部状态', value: '' },
  { text: '待复习', value: '待复习' },
  { text: '复习中', value: '复习中' },
  { text: '已完成', value: '已完成' }
])

onMounted(async () => {
  await Promise.all([
    loadNotes(),
    store.fetchTags()
  ])
})

async function loadNotes() {
  try {
    await store.fetchNotes(handbookId)
  } catch (error) {
    showToast('加载笔记失败')
  }
}

// 过滤笔记
const filteredNotes = computed(() => {
  if (!store.notes) return []
  return store.notes.filter(note => {
    const matchKeyword = !searchKeyword.value || 
      note.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      note.content.toLowerCase().includes(searchKeyword.value.toLowerCase())
    
    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.some(tag => note.tags.some(t => t.name === tag))
    
    const matchPriority = !selectedPriority.value || 
      note.priority === selectedPriority.value
    
    const matchStatus = !selectedStatus.value || 
      note.status === selectedStatus.value
    
    return matchKeyword && matchTags && matchPriority && matchStatus
  })
})

// 删除笔记
async function handleDelete(note: Note) {
  try {
    await showDialog({
      title: '确认删除',
      message: '确定要删除这个笔记吗？',
      showCancelButton: true
    })
    
    await store.deleteNote(note.id)
    showToast('删除成功')
  } catch {
    // 用户取消或删除失败
  }
}
</script>

<template>
  <div class="note-list">
    <!-- 搜索和筛选 -->
    <div class="filters">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索笔记"
        shape="round"
      />  
      <!-- 标签筛选 -->
      <div class="filter-section">
        <van-tag
          v-for="tag in store.tags"
          :key="tag.id"
          :type="selectedTags.includes(tag.name) ? 'primary' : 'default'"
          class="filter-tag"
          @click="selectedTags.includes(tag.name) 
            ? selectedTags = selectedTags.filter(t => t !== tag.name)
            : selectedTags.push(tag.name)"
        >
          {{ tag.name }}
        </van-tag>
      </div>
      
      <!-- 优先级和状态筛选 -->
      <van-row gutter="16">
        <van-col span="12">
          <van-dropdown-menu>
            <van-dropdown-item v-model="selectedPriority" :options="priorityOptions" />
          </van-dropdown-menu>
        </van-col>
        <van-col span="12">
          <van-dropdown-menu>
            <van-dropdown-item v-model="selectedStatus" :options="statusOptions" />
          </van-dropdown-menu>
        </van-col>
      </van-row>
    </div>

    <!-- 笔记列表 -->
    <div class="list">
      <van-empty v-if="!filteredNotes.length" description="暂无笔记" />
      <van-cell-group v-else>
        <van-swipe-cell
          v-for="note in filteredNotes"
          :key="note.id"
        >
          <van-cell
            :title="note.title"
            :label="note.content"
            is-link
            @click="$router.push(`/handbooks/notes/${note.id}/detail`)"
          >
            <template #label>
              <div class="note-content">{{ note.content }}</div>
            </template>
            <template #value>
              <div class="note-meta">
                <van-tag :type="note.priority === 'high' ? 'danger' : note.priority === 'medium' ? 'warning' : 'success'">
                  {{ note.priority }}
                </van-tag>
                <van-tag :type="note.status === '已完成' ? 'success' : 'primary'">
                  {{ note.status }}
                </van-tag>
                <van-tag v-for="tag in note.tags" :key="tag.id" plain>
                  {{ tag.name }}
                </van-tag>
              </div>
            </template>
          </van-cell>
          
          <template #right>
            <van-button
              square
              type="primary"
              class="edit-button"
              @click.stop="$router.push(`/handbooks/notes/${note.id}`)"
            >
              编辑
            </van-button>
            <van-button
              square
              type="danger"
              class="delete-button"
              @click.stop="handleDelete(note)"
            >
              删除
            </van-button>
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>

    <!-- 加载状态 -->
    <van-loading v-if="store.isLoading" vertical>加载中...</van-loading>
  </div>
</template>

<style lang="scss" scoped>
.note-list {
  padding: var(--van-padding-md);

  .filters {
    margin-bottom: var(--van-padding-md);
    
    .filter-section {
      margin: var(--van-padding-xs) 0;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      .filter-tag {
        cursor: pointer;
      }
    }
  }

  .note-meta {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .delete-button {
    height: 100%;
  }

  .note-content {
    display: -webkit-box;
    -webkit-line-clamp:2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.5;
    max-height: 3em; // line-height * 3 lines
    color: var(--van-text-color-2);
    font-size: var(--van-font-size-sm);
  }

  .list {
    .note-item {
      margin-bottom: 8px;
      
      &:not(:last-child) {
        border-bottom: 8px solid var(--van-gray-3);
      }
    }
  }
}
.list {
    background: var(--van-background-2);
    border-radius: var(--van-radius-md);
    padding: var(--van-padding-xs);

    :deep {
      .van-cell-group {
        background: transparent;
      }

      .van-swipe-cell {
        margin-bottom: var(--van-padding-xs);
        border-bottom: 1px solid var(--van-border-color);

        &:last-child {
          margin-bottom: 0;
          border-bottom: none;
        }
      }

      .van-cell {
        background: var(--van-background);
        border-radius: var(--van-radius-sm);
        margin: 0 var(--van-padding-xs);
        margin-bottom: var(--van-padding-xs);
        
        &::after {
          display: none;
        }

        .van-cell__title {
          color: var(--van-text-color);
          font-weight: 500;
        }
      }
    }

    .note-content {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      line-height: 1.5;
      max-height: 3em;
      color: var(--van-text-color-2);
      font-size: var(--van-font-size-sm);
      margin: var(--van-padding-xs) 0;
    }

    .note-meta {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
      margin-top: var(--van-padding-xs);

      :deep(.van-tag) {
        margin-right: var(--van-padding-xs);
      }
    }

    .edit-button {
      margin-right: var(--van-padding-xs);
      border-radius: var(--van-radius-sm);
      background: transparent;
      border: 1px solid var(--van-border-color);
      color: var(--van-text-color);
      
      &:active {
        background: var(--van-active-color);
      }
    }

    .delete-button {
      height: 100%;
      min-width: 65px;
    }
  }
</style>