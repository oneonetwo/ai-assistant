<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import Selector from '@/components/common/Selector.vue'

const store = useHandbookStore()
const name = ref('')
const categoryId = ref<number | undefined>()
const showAddCategoryPopup = ref(false)
const newCategoryName = ref('')

const props = defineProps<{
  modelValue: boolean
  handbook?: Handbook
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

// 关闭弹窗
function handleClose() {
  emit('update:modelValue', false)
  name.value = ''
  categoryId.value = undefined
}

// 提交表单
async function handleSubmit() {
  if (!name.value || !categoryId.value) {
    showToast('请填写完整信息')
    return
  }

  try {
    if (props.handbook) {
      // 更新手册
      await store.updateHandbook(props.handbook.id, {
        name: name.value,
        category_id: categoryId.value
      })
      showToast('更新成功')
    } else {
      // 创建手册
      await store.createHandbook({
        name: name.value,
        category_id: categoryId.value
      })
      showToast('创建成功')
    }
    emit('success')
    handleClose()
  } catch {
    showToast(props.handbook ? '更新失败' : '创建失败')
  }
}

// 添加新分类
async function handleAddCategory() {
  if (!newCategoryName.value) {
    showToast('请输入分类名称')
    return
  }

  try {
    await store.createCategory(newCategoryName.value)
    showToast('创建成功')
    newCategoryName.value = ''
    showAddCategoryPopup.value = false
  } catch {
    showToast('创建失败')
  }
}

// 组件初始化时设置默认分类
onMounted(() => {
})
watch(() => store.categories, (newCategories) => {
    if (newCategories.length > 0 && !categoryId.value) {
        categoryId.value = store.categories[0].id   
    }
})

// 监听 handbook 变化，设置初始值
watch(() => props.handbook, (newHandbook) => {
  if (newHandbook) {
    name.value = newHandbook.name
    categoryId.value = newHandbook.category_id
  } else {
    name.value = ''
    categoryId.value = undefined
  }
}, { immediate: true })
</script>

<template>
  <van-popup
    :show="modelValue"
    round
    position="center"
    :style="{ width: '90%', maxWidth: '500px' }"
    close-on-click-overlay
  >
    <div class="handbook-form">
      <div class="header">
        <h3>{{ props.handbook ? '编辑手册' : '创建手册' }}</h3>
        <van-icon name="cross" @click="handleClose" />
      </div>

      <div class="form-content">
        <van-form @submit="handleSubmit">
          <van-cell-group inset>
            <!-- 手册名称 -->
            <van-field
              v-model="name"
              label="手册名称"
              placeholder="请输入手册名称"
              :rules="[{ required: true, message: '请输入手册名称' }]"
            />

            <!-- 分类选择 -->

            <div class="category-field">
              <span class="category-label">所属分类</span>
              <Selector
                v-model="categoryId"
                :options="store.categories.map(c => ({
                  text: c.name,
                  value: c.id
                }))"
                placeholder="请选择分类"
              />
              <van-button 
                size="small" 
                type="primary" 
                @click="showAddCategoryPopup = true"
              >
                添加分类
              </van-button>
            </div>
          </van-cell-group>

          <!-- 提交按钮 -->
          <div class="submit-btn">
            <van-button
              round
              block
              type="primary"
              native-type="submit"
              :loading="store.isLoading"
            >
              {{ props.handbook ? '更新' : '创建' }}
            </van-button>
          </div>
        </van-form>

        <!-- 添加分类弹窗 -->
        <van-popup
          v-model:show="showAddCategoryPopup"
          round
          position="center"
          :style="{ width: '80%', maxWidth: '300px' }"
        >
          <div class="add-category-popup">
            <div class="popup-header">
              <h4>新建分类</h4>
              <van-icon name="cross" @click="showAddCategoryPopup = false" />
            </div>
            <div class="popup-content">
              <van-field
                v-model="newCategoryName"
                placeholder="请输入分类名称"
                :rules="[{ required: true, message: '请输入分类名称' }]"
              />
              <div class="popup-buttons">
                <van-button 
                  round 
                  block 
                  type="primary" 
                  @click="handleAddCategory"
                >
                  确认
                </van-button>
              </div>
            </div>
          </div>
        </van-popup>
      </div>
    </div>
  </van-popup>
</template>

<style lang="scss" scoped>
.handbook-form {
  background: var(--van-background-2);
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--van-padding-md);
    border-bottom: 1px solid var(--van-border-color);
    
    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--van-text-color);
    }
    
    .van-icon {
      font-size: 20px;
      cursor: pointer;
      color: var(--van-gray-6);
      
      &:hover {
        color: var(--van-gray-8);
      }
    }
  }

  .form-content {
    padding: var(--van-padding-md);

    .van-cell-group {
      margin-bottom: var(--van-padding-md);
      overflow: visible;
    }
  }

  .category-field {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: var(--van-padding-xs) var(--van-padding-md);
    background: #444654;
    
    .custom-selector {
      flex: 1;
    }
    
    .van-button {
      flex-shrink: 0;
    }
  }

  .submit-btn {
    margin-top: var(--van-padding-lg);
    padding: 0 var(--van-padding-md);
    
    .van-button {
      height: 40px;
      font-size: 16px;
    }
  }
}

.add-category-popup {
  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--van-padding-md);
    border-bottom: 1px solid var(--van-border-color);

    h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .van-icon {
      cursor: pointer;
      color: var(--van-gray-6);
      
      &:hover {
        color: var(--van-gray-8);
      }
    }
  }

  .popup-content {
    padding: var(--van-padding-md);

    .popup-buttons {
      margin-top: var(--van-padding-lg);
    }
  }
}
.category-label {
  margin-right: 20px;
  font-size: 14px;
}
</style> 