<script setup lang="ts">
import { ref } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'

// 添加 showCategoryPicker ref
const showCategoryPicker = ref(false)
const categoryPicker = ref()

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const store = useHandbookStore()
const name = ref('')
const categoryId = ref<number>()

// 关闭弹窗
function handleClose() {
  emit('update:modelValue', false)
  // 重置表单
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
    await store.createHandbook(name.value, categoryId.value)
    showToast('创建成功')
    emit('success')
    handleClose()
  } catch {
    showToast('创建失败')
  }
}
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
        <h3>创建手册</h3>
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
            <van-field
              v-model="categoryId"
              label="所属分类"
              placeholder="请选择分类"
              readonly
              is-link
              :rules="[{ required: true, message: '请选择分类' }]"
              @click="showCategoryPicker = true"
            >
              <template #input>
                <span v-if="categoryId">
                  {{ store.categories.find(c => c.id === categoryId)?.name }}
                </span>
              </template>
            </van-field>
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
              创建
            </van-button>
          </div>
        </van-form>

        <!-- 分类选择器 -->
        <van-popup
          v-model:show="showCategoryPicker"
          round
          position="bottom"
        >
          <van-picker
            ref="categoryPicker"
            :columns="store.categories.map(c => ({
              text: c.name,
              value: c.id
            }))"
            :default-index="0"
            title="选择分类"
            @confirm="(value) => {
              categoryId = value.value
              showCategoryPicker = false
            }"
            @cancel="showCategoryPicker = false"
          />
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
</style> 