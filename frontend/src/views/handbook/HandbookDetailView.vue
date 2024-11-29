<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import NoteList from '@/components/handbook/NoteList.vue'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()
const handbookId = route.params.id as string

onMounted(async () => {
  try {
    await store.getHandbook(Number(handbookId))
    // await store.fetchNotes(Number(handbookId))
  } catch (error) {
    showToast('加载失败')
    // router.push('/handbooks')
  }
})
</script>

<template>
  <div class="handbook-detail-view">
    <van-nav-bar
      :title="store.currentHandbook?.title || '加载中...'"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <van-button 
          type="primary" 
          size="small"
          icon="plus"
          @click="router.push(`/notes/new?handbook=${handbookId}`)"
        >
          新建笔记
        </van-button>
      </template>
    </van-nav-bar>
    
    <NoteList />
  </div>
</template>

<style lang="scss" scoped>
.handbook-detail-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 