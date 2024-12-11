<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { RevisionPlan } from '@/types/revision'
import type { Note } from '@/types/handbook'

const router = useRouter()
const revisionStore = useRevisionStore()
const handbookStore = useHandbookStore()

const formData = ref({
  name: '',
  start_date: '',
  end_date: '',
  category_id: -1,
  handbook_ids: [] as number[],
  tag_ids: [] as number[],
  note_statuses: [] as string[]
})

const statusOptions = [
  { text: '草稿', value: 'draft' },
  { text: '已发布', value: 'published' },
  { text: '已归档', value: 'archived' }
]

// 表单验证
function validateDates() {
  if (!formData.value.start_date || !formData.value.end_date) return true
  const start = new Date(formData.value.start_date)
  const end = new Date(formData.value.end_date)
  return end >= start
}

// Add computed properties for filtered handbooks
const filteredHandbooks = computed(() => {
  if (formData.value.category_id === -1) {
    return handbookStore.handbooks
  }
  return handbookStore.handbooks.filter(
    handbook => handbook.category_id === formData.value.category_id
  )
})

// Watch category changes to update handbook selection
watch(() => formData.value.category_id, (newCategoryId) => {
  // Select all handbooks in the current category
  formData.value.handbook_ids = filteredHandbooks.value.map(h => h.id)
})

// Add color cycling function
function getColorByTagId(id: number): number {
  return (id % 5) + 1
}

// 在现有的 imports 中添加
import type { Note } from '@/types/handbook'

// 在 setup 中添加
const notes = ref<Note[]>([])

// 在 onMounted 中添加获取笔记的逻辑
onMounted(async () => {
  try {
    await handbookStore.fetchHandbooks()
    await handbookStore.fetchCategories()
    await handbookStore.fetchTags()
    
    // 设置初始值
    formData.value.category_id = -1
    formData.value.handbook_ids = handbookStore.handbooks.map(h => h.id)
    formData.value.tag_ids = []
    
    // 获取所有笔记
    await handbookStore.fetchNotes()
    notes.value = handbookStore.notes
  } catch (error) {
    showToast('加载数据失败')
  }
})

// 添加计算属性来过滤笔记
const filteredNotes = computed(() => {
  if (!notes.value) return []
  return notes.value.filter(note => {
    const matchHandbook = formData.value.handbook_ids.includes(note.handbook_id)
    const matchStatus = formData.value.note_statuses.length === 0 || 
      formData.value.note_statuses.includes(note.status)
    const matchTags = formData.value.tag_ids.length === 0 ||
      formData.value.tag_ids.some(tagId => 
        note.tags.some(t => t.id === tagId)
      )
    return matchHandbook && matchStatus && matchTags
  })
})

// 提交表单
async function handleSubmit() {
  try {
    if (!formData.value.name.trim()) {
      showToast('请输入计划名称')
      return
    }
    if (formData.value.handbook_ids.length === 0) {
      showToast('请选择至少一个手册')
      return
    }
    // 添加笔记验证
    if (filteredNotes.value.length === 0) {
      showToast('当前筛选条件下没有可用的笔记，请调整筛选条件')
      return
    }
    await revisionStore.createPlan(formData.value)
    showToast('创建成功')
    router.push({ name: 'revision-plans' })
  } catch (error) {
    showToast('创建失败')
  }
}

// 在 script setup 中添加
const isNotesExpanded = ref(false)
</script>

<template>
  <div class="plan-editor">
    <van-nav-bar
      title="新建复习计划"
      left-arrow
      @click-left="router.back()"
    />

    <div class="editor-content">
      <van-form @submit="handleSubmit">
        <van-cell-group inset>
          <van-field
            v-model="formData.name"
            label="计划名称"
            placeholder="请输入计划名称称"
            :rules="[{ required: true, message: '请输入计划名称' }]"
          />

          <van-field
            v-model="formData.start_date"
            label="开始日期"
            type="date"
            :rules="[
              { required: true, message: '请选择开始日期' },
              { validator: validateDates, message: '结束日期不能早于开始日期' }
            ]"
          />

          <van-field
            v-model="formData.end_date"
            label="结束日期"
            type="date"
            :rules="[
              { required: true, message: '请选择结束日期' },
              { validator: validateDates, message: '结束日期不能早于开始日期' }
            ]"
          />

          <van-field name="categories" label="选择分类">
            <template #input>
              <van-radio-group v-model="formData.category_id">
                <van-radio :name="-1">全部</van-radio>
                <van-radio
                  v-for="category in handbookStore.categories"
                  :key="category.id"
                  :name="category.id"
                >
                  {{ category.name }}
                </van-radio>
              </van-radio-group>
            </template>
          </van-field>

          <van-field 
            name="handbook" 
            label="选择手册"
            :rules="[{ required: true, message: '请至少选择一个手册' }]"
          >
            <template #input>
              <div class="handbook-selector">
                <div class="handbook-count">
                  已选择 {{ formData.handbook_ids.length }} 个手册
                </div>
                <van-checkbox-group v-model="formData.handbook_ids">
                  <div 
                    v-for="handbook in filteredHandbooks" 
                    :key="handbook.id"
                    class="handbook-item"
                  >
                    <van-checkbox 
                      :name="handbook.id"
                      class="handbook-checkbox"
                    >
                      <div class="handbook-info">
                        <span class="handbook-name">{{ handbook.name }}</span>
                      </div>
                    </van-checkbox>
                  </div>
                </van-checkbox-group>
              </div>
            </template>
          </van-field>

          <van-field name="tags" label="选择标签">
            <template #input>
              <div class="tag-selector">
                <div class="tag-count">
                  已选择 {{ formData.tag_ids.length }} 个标签
                </div>
                <van-checkbox-group v-model="formData.tag_ids">
                  <van-checkbox
                    v-for="tag in handbookStore.tags"
                    :key="tag.id"
                    :name="tag.id"
                    class="tag-checkbox"
                  >
                    <div :class="['custom-tag', `color-${getColorByTagId(tag.id)}`, { 'is-selected': formData.tag_ids.includes(tag.id) }]">
                      {{ tag.name }}
                    </div>
                  </van-checkbox>
                </van-checkbox-group>
              </div>
            </template>
          </van-field>

          <van-field name="note_statuses" label="笔记状态">
            <template #input>
              <van-checkbox-group v-model="formData.note_statuses">
                <van-checkbox
                  v-for="option in statusOptions"
                  :key="option.value"
                  :name="option.value"
                >
                  {{ option.text }}
                </van-checkbox>
              </van-checkbox-group>
            </template>
          </van-field>

          <van-field name="notes" label="包含的笔记">
            <template #input>
              <div class="notes-preview">
                <div class="notes-header" @click="isNotesExpanded = !isNotesExpanded">
                  <span class="notes-count">共 {{ filteredNotes.length }} 个笔记</span>
                  <span v-if="filteredNotes.length === 0" class="error-text">
                    (请调整筛选条件)
                  </span>
                  <van-icon 
                    :name="isNotesExpanded ? 'arrow-up' : 'arrow-down'" 
                    class="expand-icon"
                  />
                </div>
                <collapse-transition>
                  <van-cell-group 
                    inset 
                    v-show="isNotesExpanded"
                    class="notes-list"
                  >
                    <template v-if="filteredNotes.length">
                      <van-cell
                        v-for="note in filteredNotes"
                        :key="note.id"
                        :title="note.title"
                      />
                    </template>
                    <van-empty v-else description="暂无符合条件的笔记" />
                  </van-cell-group>
                </collapse-transition>
              </div>
            </template>
          </van-field>
        </van-cell-group>

        <div class="submit-btn">
          <van-button
            type="primary"
            block
            native-type="submit"
            :loading="revisionStore.isLoading"
          >
            创建计划
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.plan-editor {
  height: 100%;
  display: flex;
  flex-direction: column;

  .editor-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .duration-unit {
    margin-left: 8px;
    color: var(--van-text-color-2);
  }

  .submit-btn {
    margin-top: 24px;
    padding: 0 16px;
  }

  :deep {
    .van-radio-group {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 8px 0;
    }
    
    .van-checkbox-group {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 8px 0;
    }

    .handbook-selector {
      padding: 8px 0;

      .handbook-count {
        font-size: 14px;
        color: var(--van-gray-6);
        margin-bottom: 12px;
      }

      .handbook-item {
        margin-bottom: 12px;
        background: var(--van-background-2);
        border-radius: 8px;
        transition: all 0.3s ease;

        &:last-child {
          margin-bottom: 0;
        }

        .van-checkbox {
          width: 100%;
          padding: 12px;
        }

        .handbook-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .handbook-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--van-text-color);
        }

        .handbook-meta {
          font-size: 12px;
          color: var(--van-gray-6);
        }
      }

      .van-checkbox__label {
        flex: 1;
      }

      .van-checkbox__icon {
        flex-shrink: 0;
      }

      // 选中状态样式
      .van-checkbox__icon--checked + .van-checkbox__label {
        .handbook-item {
          background: var(--van-primary-light);
        }
        
        .handbook-name {
          color: var(--van-primary);
        }
      }
    }

    .tag-selector {
      padding: 8px 0;

      .tag-count {
        font-size: 14px;
        color: var(--van-gray-6);
        margin-bottom: 12px;
      }

      .van-checkbox-group {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .tag-checkbox {
        margin: 0 !important;
        padding: 0 !important;

        // ��藏默认的复选框图标
        .van-checkbox__icon {
          display: none;
        }
      }
    }
  }

  .custom-tag {
    border-radius: 16px !important;
    padding: 2px 8px !important;
    margin: 4px !important;
    border: none !important;
    font-size: 12px !important;
    cursor: pointer;
    transition: all 0.3s ease;
    background-color: transparent !important;
    border: 0.5px solid transparent !important;
    
    &.color-1 {
      color: #00B4DB !important;
      border-color: #00B4DB !important;
      
      &.is-selected {
        background-color: #00B4DB !important;
        color: #ffffff !important;
      }
    }
    
    &.color-2 {
      color: #2C5E1A !important;
      border-color: #9BE36D !important;
      
      &.is-selected {
        background-color: #9BE36D !important;
        color: #2C5E1A !important;
      }
    }
    
    &.color-3 {
      color: #A78BFA !important;
      border-color: #A78BFA !important;
      
      &.is-selected {
        background-color: #A78BFA !important;
        color: #ffffff !important;
      }
    }
    
    &.color-4 {
      color: #FF8C82 !important;
      border-color: #FF8C82 !important;
      
      &.is-selected {
        background-color: #FF8C82 !important;
        color: #ffffff !important;
      }
    }
    
    &.color-5 {
      color: #14B8A6 !important;
      border-color: #14B8A6 !important;
      
      &.is-selected {
        background-color: #14B8A6 !important;
        color: #ffffff !important;
      }
    }
  }

  .notes-preview {
    padding: 8px 0;

    .notes-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      background: var(--van-background-2);
      border-radius: var(--van-radius-md);
      cursor: pointer;
      transition: background-color 0.3s;
      margin-bottom: 8px;
      
      &:active {
        background: var(--van-active-color);
      }

      .notes-count {
        font-size: 14px;
        color: var(--van-text-color);
        font-weight: 500;
      }

      .expand-icon {
        color: var(--van-gray-6);
        transition: transform 0.3s;
      }
    }

    .notes-list {
      margin-top: 8px;
      max-height: 300px;
      overflow-y: auto;
      background: var(--van-background-2);
      border-radius: var(--van-radius-md);
      
      :deep {
        .van-cell {
          background: transparent;
          
          &:not(:last-child) {
            &::after {
              border-bottom: 0.5px solid var(--van-border-color);
            }
          }
          
          .van-cell__title {
            font-size: 14px;
            color: var(--van-text-color);
            
            span {
              display: inline-block;
              max-width: 100%;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }
          }
        }

        .van-empty {
          padding: 32px 0;
          background: transparent;
        }
      }

      &::-webkit-scrollbar {
        width: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background-color: var(--van-gray-5);
        border-radius: 2px;
      }

      &::-webkit-scrollbar-track {
        background-color: transparent;
      }
    }
  }
}
.error-text {
  color: var(--van-danger-color);
  font-size: 12px;
  margin-left: 4px;
}
// 暗色主题适配
:root[data-theme='dark'] {
  .plan-editor {
    .custom-tag {
      &.color-1,
      &.color-2,
      &.color-3,
      &.color-4,
      &.color-5 {
        &:not(.is-selected) {
          color: #ffffff !important;
        }
      }
    }
  }

  .notes-preview {
    .notes-header {
      &:active {
        background: var(--van-active-color);
      }
    }
  }
}
</style> 