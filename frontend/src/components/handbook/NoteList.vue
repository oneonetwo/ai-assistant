<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
  return store.notes.filter(note => {
    const matchKeyword = !searchKeyword.value || 
      note.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      note.content.toLowerCase().includes(searchKeyword.value.toLowerCase())
    
    const matchTags = selectedTags.value.length === 0 ||
      selectedTags.value.some(tag => note.tags.includes(tag))
    
    const matchPriority = !selectedPriority.value || 
      note.priority === selectedPriority.value
    
    const matchStatus = !selectedStatus.value || 
      note.status === selectedStatus.value
    
    return matchKeyword && matchTags && matchPriority && matchStatus
  })
})

async function handleCreate() {
  try {
    const title = await showDialog({
      title: '创建笔记',
      message: '请输入笔记标题',
      showCancelButton: true,
      confirmButtonText: '创建'
    })
    
    if (title) {
      await store.createNote(handbookId, { 
        title,
        content: '',
        tags: [],
        priority: 'medium',
        status: 'draft'
      })
      showToast('创建成功')
    }
  } catch {
    // 用户取消
  }
}

async function handleDelete(note: Note) {
  try {
    await showDialog({
      title: '删除笔记',
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
    <div class="header">
      <h2>笔记列表</h2>
      <van-button 
        type="primary" 
        size="small"
        icon="plus"
        @click="handleCreate"
      >
        新建笔记
      </van-button>
    </div>

    <div class="filters">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索笔记"
        shape="round"
      />
      
      <div class="filter-tags">
        <van-dropdown-menu>
          <van-dropdown-item v-model="selectedPriority" :options="[
            { text: '全部优先级', value: '' },
            { text: '低优先级', value: 'low' },
            { text: '中优先级', value: 'medium' },
            { text: '高优先级', value: 'high' }
          ]" />
          
          <van-dropdown-item v-model="selectedStatus" :options="[
            { text: '全部状态', value: '' },
            { text: '草稿', value: 'draft' },
            { text: '已发布', value: 'published' },
            { text: '已归档', value: 'archived' }
          ]" />
        </van-dropdown-menu>
        
        <van-tag
          v-for="tag in store.tags"
          :key="tag.id"
          :type="selectedTags.includes(tag.name) ? 'primary' : 'default'"
          class="filter-tag"
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

    <div class="list">
      <van-cell-group>
        <van-swipe-cell
          v-for="note in filteredNotes"
          :key="note.id"
        >
          <van-cell
            :title="note.title"
            :label="note.content.slice(0, 50) + (note.content.length > 50 ? '...' : '')"
            is-link
            :to="`/notes/${note.id}`"
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
          
          <template #right>
            <van-button
              square
              type="danger"
              class="delete-button"
              @click="handleDelete(note)"
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
.note-list {
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

  .filters {
    margin-bottom: var(--van-padding-md);
    
    .filter-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: var(--van-padding-xs);
      
      .filter-tag {
        cursor: pointer;
      }
    }
  }

  .note-meta {
    display: flex;
    gap: 4px;
  }

  .delete-button {
    height: 100%;
  }
}
</style>