<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
  handbook_ids: [] as number[],
  category_ids: [] as number[],
  tag_ids: [] as number[],
  note_statuses: [] as string[]
})

// 加载手册数据
onMounted(async () => {
  try {
    await handbookStore.fetchHandbooks()
    await handbookStore.fetchCategories()
    await handbookStore.fetchTags()
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
            placeholder="请输入计划名称"
            :rules="[{ required: true, message: '请输入计划名称' }]"
          />

          <van-field
            v-model="formData.start_date"
            label="开始日期"
            type="date"
            :rules="[{ required: true, message: '请选择开始日期' }]"
          />

          <van-field
            v-model="formData.end_date"
            label="结束日期"
            type="date"
            :rules="[{ required: true, message: '请选择结束日期' }]"
          />

          <van-field name="handbook" label="选择手册">
            <template #input>
              <van-checkbox-group v-model="formData.handbook_ids">
                <van-checkbox
                  v-for="handbook in handbookStore.handbooks"
                  :key="handbook.id"
                  :name="handbook.id"
                >
                  {{ handbook.name }}
                </van-checkbox>
              </van-checkbox-group>
            </template>
          </van-field>

          <van-field name="categories" label="选择分类">
            <template #input>
              <van-checkbox-group v-model="formData.category_ids">
                <van-checkbox
                  v-for="category in handbookStore.categories"
                  :key="category.id"
                  :name="category.id"
                >
                  {{ category.name }}
                </van-checkbox>
              </van-checkbox-group>
            </template>
          </van-field>

          <van-field name="tags" label="选择标签">
            <template #input>
              <van-checkbox-group v-model="formData.tag_ids">
                <van-checkbox
                  v-for="tag in handbookStore.tags"
                  :key="tag.id"
                  :name="tag.id"
                >
                  {{ tag.name }}
                </van-checkbox>
              </van-checkbox-group>
            </template>
          </van-field>

          <van-field name="note_statuses" label="笔记状态">
            <template #input>
              <van-checkbox-group v-model="formData.note_statuses">
                <van-checkbox name="draft">草稿</van-checkbox>
                <van-checkbox name="published">已发布</van-checkbox>
                <van-checkbox name="archived">已归档</van-checkbox>
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

  :deep(.van-checkbox-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px 0;
  }

  :deep(.van-radio-group) {
    display: flex;
    gap: 16px;
  }
}
</style> 