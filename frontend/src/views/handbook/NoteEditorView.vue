<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NoteEditor from '@/components/handbook/NoteEditor.vue'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()
const noteId = route.params.id as string
const isNew = route.fullPath.includes('/new')
onMounted(async () => {
  if (!isNew) {
    try {
      await store.fetchNote(Number(noteId))
    } catch (error) {
      showToast('加载笔记失败')
      // router.back()
    }
  }
})
</script>

<template>
  <div class="note-editor-view">
    <van-nav-bar
      v-if="!isNew"
      left-arrow
      @click-left="router.back()"
    />
    <NoteEditor />
  </div>
</template>

<style lang="scss" scoped>
.note-editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 