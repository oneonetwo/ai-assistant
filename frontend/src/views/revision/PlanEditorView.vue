<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRevisionStore } from '@/stores/revision'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { RevisionPlan } from '@/types/revision'

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

// 加载手册数据
onMounted(async () => {
  try {
    await handbookStore.fetchHandbooks()
    await handbookStore.fetchCategories()
    await handbookStore.fetchTags()
    
    // Set initial values
    formData.value.category_id = -1
    formData.value.handbook_ids = handbookStore.handbooks.map(h => h.id)
    formData.value.tag_ids = [] // 默认不选中任何标签
  } catch (error) {
    showToast('加载数据失败')
  }
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

    await revisionStore.createPlan(formData.value)
    showToast('创建成功')
    router.push({ name: 'revision-plans' })
  } catch (error) {
    showToast('创建失败')
  }
}
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

        // 隐藏默认的复选框图标
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
}
</style> 