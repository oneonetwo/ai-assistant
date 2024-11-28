<script setup lang="ts">
import { onMounted } from 'vue'
import { useHandbookStore } from '@/stores/handbook'
import { showDialog, showToast } from 'vant'
import type { Handbook } from '@/types/handbook'

const store = useHandbookStore()

onMounted(() => {
  loadHandbooks()
})

async function loadHandbooks() {
  try {
    await store.fetchHandbooks()
  } catch (error) {
    showToast('加载手册失败')
  }
}

async function handleCreate() {
  try {
    const title = await showDialog({
      title: '创建手册',
      message: '请输入手册标题',
      showCancelButton: true,
      confirmButtonText: '创建'
    })
    
    if (title) {
      await store.createHandbook({ title })
      showToast('创建成功')
    }
  } catch {
    // 用户取消
  }
}

async function handleDelete(handbook: Handbook) {
  try {
    await showDialog({
      title: '删除手册',
      message: '确定要删除这个手册吗？',
      showCancelButton: true
    })
    
    await store.deleteHandbook(handbook.id)
    showToast('删除成功')
  } catch {
    // 用户取消或删除失败
  }
}

async function handleRename(handbook: Handbook) {
  try {
    const title = await showDialog({
      title: '重命名手册',
      message: '请输入新的标题',
      showCancelButton: true,
      confirmButtonText: '确定'
    })
    
    if (title) {
      await store.updateHandbook(handbook.id, { title })
      showToast('重命名成功')
    }
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <div class="handbook-list">
    <div class="header">
      <h2>知识手册</h2>
      <van-button 
        type="primary" 
        size="small"
        icon="plus"
        @click="handleCreate"
      >
        新建手册
      </van-button>
    </div>

    <div class="list">
      <van-cell-group>
        <van-swipe-cell
          v-for="handbook in store.handbooks"
          :key="handbook.id"
        >
          <van-cell
            :title="handbook.title"
            :label="handbook.description || '暂无描述'"
            is-link
            :to="`/handbooks/${handbook.id}`"
          >
            <template #right-icon>
              <van-button 
                size="small"
                icon="edit"
                @click.stop="handleRename(handbook)"
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
  </div>
</template>

<style lang="scss" scoped>
.handbook-list {
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

  .delete-button {
    height: 100%;
  }
}
</style> 