<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { showToast } from 'vant'
import type { Note } from '@/types/handbook'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()
const noteId = route.params.id as string

const note = ref<Note | null>(null)
const title = ref('')
const content = ref('')
const selectedTags = ref<string[]>([])
const priority = ref<Note['priority']>('medium')
const status = ref<Note['status']>('draft')

onMounted(async () => {
  if (noteId !== 'new') {
    await loadNote()
  }
  await store.fetchTags()
})

async function loadNote() {
  try {
    const response = await store.fetchNote(noteId)
    note.value = response
    title.value = response.title
    content.value = response.content
    selectedTags.value = response.tags
    priority.value = response.priority
    status.value = response.status
  } catch (error) {
    showToast('加载笔记失败')
    router.back()
  }
}

async function handleSave() {
  try {
    const data = {
      title: title.value,
      content: content.value,
      tags: selectedTags.value,
      priority: priority.value,
      status: status.value
    }
    
    if (noteId === 'new') {
      await store.createNote(route.params.handbookId as string, data)
    } else {
      await store.updateNote(noteId, data)
    }
    
    showToast('保存成功')
    router.back()
  } catch (error) {
    showToast('保存失败')
  }
}

async function handleUpload(file: File) {
  try {
    if (!note.value) return
    await store.uploadAttachment(note.value.id, file)
    showToast('上传成功')
    await loadNote() // 重新加载笔记以获取最新附件
  } catch (error) {
    showToast('上传失败')
  }
}

async function handleDeleteAttachment(attachmentId: string) {
  try {
    await store.deleteAttachment(attachmentId)
    showToast('删除成功')
    await loadNote() // 重新加载笔记以更新附件列表
  } catch (error) {
    showToast('删除失败')
  }
}
</script>

<template>
  <div class="note-editor">
    <van-nav-bar
      :title="noteId === 'new' ? '新建笔记' : '编辑笔记'"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <van-button 
          type="primary" 
          size="small"
          @click="handleSave"
        >
          ��存
        </van-button>
      </template>
    </van-nav-bar>

    <div class="editor-content">
      <van-field
        v-model="title"
        label="标题"
        placeholder="请输入笔记标题"
      />
      
      <van-field
        v-model="content"
        type="textarea"
        label="内容"
        placeholder="请输入笔记内容"
        rows="10"
        autosize
      />
      
      <van-field label="标签">
        <template #input>
          <div class="tag-selector">
            <van-tag
              v-for="tag in store.tags"
              :key="tag.id"
              :type="selectedTags.includes(tag.name) ? 'primary' : 'default'"
              class="tag-item"
              @click="
                selectedTags.includes(tag.name)
                  ? selectedTags = selectedTags.filter(t => t !== tag.name)
                  : selectedTags.push(tag.name)
              "
            >
              {{ tag.name }}
            </van-tag>
          </div>
        </template>
      </van-field>
      
      <van-field label="优先级">
        <template #input>
          <van-radio-group v-model="priority" direction="horizontal">
            <van-radio name="low">低</van-radio>
            <van-radio name="medium">中</van-radio>
            <van-radio name="high">高</van-radio>
          </van-radio-group>
        </template>
      </van-field>
      
      <van-field label="状态">
        <template #input>
          <van-radio-group v-model="status" direction="horizontal">
            <van-radio name="draft">草稿</van-radio>
            <van-radio name="published">已发布</van-radio>
            <van-radio name="archived">已归档</van-radio>
          </van-radio-group>
        </template>
      </van-field>
      
      <div class="attachments">
        <div class="section-title">附件</div>
        <van-uploader
          :after-read="handleUpload"
          multiple
        />
        
        <div v-if="note?.attachments.length" class="attachment-list">
          <van-cell-group>
            <van-swipe-cell
              v-for="attachment in note.attachments"
              :key="attachment.id"
            >
              <van-cell
                :title="attachment.name"
                :label="`${(attachment.size / 1024).toFixed(2)}KB`"
              >
                <template #right-icon>
                  <van-button 
                    size="small"
                    icon="down"
                    @click="window.open(attachment.url)"
                  />
                </template>
              </van-cell>
              
              <template #right>
                <van-button
                  square
                  type="danger"
                  class="delete-button"
                  @click="handleDeleteAttachment(attachment.id)"
                >
                  删除
                </van-button>
              </template>
            </van-swipe-cell>
          </van-cell-group>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.note-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;

  .editor-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--van-padding-md);
  }

  .tag-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .tag-item {
      cursor: pointer;
    }
  }

  .attachments {
    margin-top: var(--van-padding-md);
    
    .section-title {
      margin-bottom: var(--van-padding-xs);
      font-weight: 500;
    }
    
    .attachment-list {
      margin-top: var(--van-padding-xs);
    }
  }

  .delete-button {
    height: 100%;
  }
}
</style> 