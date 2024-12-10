<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showDialog, showToast } from 'vant'
import { useRouter } from 'vue-router'
import type { Handbook } from '@/types/handbook'
import HandbookForm from './HandbookForm.vue'

const router = useRouter()
const store = useHandbookStore()
const selectedCategoryId = ref<number | null>(null)

// 创建手册弹窗
const showCreateForm = ref(false)

// 编辑手册弹窗
const showEditForm = ref(false)
const editingHandbook = ref<Handbook>()

onMounted(async () => {
  await Promise.all([
    loadHandbooks(),
    loadCategories()
  ])
})

// 加载数据
async function loadHandbooks() {
  try {
    await store.fetchHandbooks(selectedCategoryId.value)
  } catch (error) {
    showToast('加载手册失败')
  }
}

async function loadCategories() {
  try {
    await store.fetchCategories()
    console.log('store.categories>>>>', store.categories)
  } catch (error) {
    showToast('加载分类失败')
  }
}

// 分类切换
async function handleCategoryChange(categoryId: number | null) {
  selectedCategoryId.value = categoryId
  await loadHandbooks()
}

// 创建手册成功回调
async function handleCreateSuccess() {
  await loadHandbooks()
}

// 编辑手册
function handleEdit(handbook: Handbook) {
  editingHandbook.value = handbook
  showEditForm.value = true
}

// 删除手册
async function handleDelete(handbook: Handbook) {
  try {
    await showDialog({
      title: '确认删除',
      message: `是否确认删除手册"${handbook.name}"？`,
      showCancelButton: true
    })
    
    await store.deleteHandbook(handbook.id)
    showToast('删除成功')
    await loadHandbooks()
  } catch (error) {
    if (error) {
      showToast('删除失败')
    }
  }
}

// 编辑手册成功回调
async function handleEditSuccess() {
  await loadHandbooks()
  showEditForm.value = false
  editingHandbook.value = undefined
}
</script>

<template>
  <div class="handbook-list">
    <!-- 顶部操作栏 -->
    <div class="header">
      <h2 class="title">知识手册</h2>
      <van-button 
        type="primary" 
        size="small"
        icon="plus"
        class="create-button"
        @click="showCreateForm = true"
      >
        新建手册
      </van-button>
    </div>

    <!-- 分类选择 -->
    <div class="categories" v-if="store.categories.length">
      <van-tabs 
        v-model:active="selectedCategoryId" 
        @change="handleCategoryChange"
        class="custom-tabs"
      >
        <van-tab 
          title="全部"
          :name="null"
        />
        <van-tab 
          v-for="category in store.categories" 
          :key="category.id"
          :title="category.name"
          :name="category.id"
        />
      </van-tabs>
    </div>

    <!-- 手册列表 -->
    <div class="list-container">
      <van-empty v-if="!store.handbooks.length" description="暂无手册" />
      <van-cell-group v-else class="handbook-cells">
        <van-swipe-cell
          v-for="handbook in store.handbooks"
          :key="handbook.id"
          class="handbook-item"
        >
          <van-cell
            :title="handbook.name"
            is-link
            @click="router.push(`/handbooks/${handbook.id}`)"
          >
            <template #right-icon>
              <van-button 
                size="small"
                icon="edit"
                class="edit-button"
                @click.stop="handleEdit(handbook)"
              />
            </template>
          </van-cell>
          
          <template #right>
            <van-button
              square
              type="danger"
              class="delete-button"
              @click="handleDelete(handbook)"
            >
              删除
            </van-button>
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>

    <!-- 加载状态 -->
    <van-loading v-if="store.isLoading" vertical>加载中...</van-loading>

    <!-- 创建手册表单 -->
    <HandbookForm
      :modelValue="showCreateForm"
      @success="handleCreateSuccess"
      @update:model-value="showCreateForm = $event"
    />

    <!-- 编辑手册表单 -->
    <HandbookForm
      :modelValue="showEditForm"
      @success="handleEditSuccess"
      @update:model-value="showEditForm = $event"
      :handbook="editingHandbook"
    />
  </div>
</template>

<style lang="scss" scoped>
.handbook-list {
  padding: var(--van-padding-md);
  min-height: 100vh;
  background: var(--van-background);

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--van-padding-lg);
    padding: var(--van-padding-sm) 0;
    border-bottom: 1px solid var(--van-border-color);
    
    .title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: var(--van-text-color);
    }

    .create-button {
      border-radius: var(--van-radius-md);
    }
  }

  .categories {
    margin-bottom: var(--van-padding-lg);
    background: var(--van-background-2);
    border-radius: var(--van-radius-md);
    padding: var(--van-padding-xs);

    :deep {
      .van-tabs__wrap {
        height: 44px;
      }

      .van-tab {
        color: var(--van-text-color-2);
        font-size: 14px;
        
        &--active {
          color: var(--van-primary-color);
          font-weight: 500;
        }
      }

      .van-tabs__line {
        background-color: var(--van-primary-color);
      }
    }
  }

  .list-container {
    background: var(--van-background-2);
    border-radius: var(--van-radius-md);
    padding: var(--van-padding-xs);

    .handbook-cells {
      background: transparent;

      .handbook-item {
        margin-bottom: var(--van-padding-xs);
        border-bottom: 1px solid var(--van-border-color);
        
        &:last-child {
          margin-bottom: 0;
          border-bottom: none;
        }

        :deep {
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
    }
  }

  // Loading 样式
  :deep {
    .van-loading {
      margin: var(--van-padding-lg) auto;
      color: var(--van-text-color-2);
    }
  }
}

// 深色主题适配
:root[data-theme="dark"] {
  .handbook-list {
    .list-container {
      .handbook-cells {
        .handbook-item {
          border-bottom: 1px solid var(--van-gray-8);
          
          :deep {
            .van-cell {
              background: var(--van-background-2);
            }
          }

          .edit-button {
            background: transparent;
            border-color: var(--van-gray-7);
            color: var(--van-gray-5);
            
            &:active {
              background: var(--van-gray-8);
            }
          }
        }
      }
    }
  }
}
</style> 