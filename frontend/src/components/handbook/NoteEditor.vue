<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { useNoteEditorStore } from '@/stores/noteEditor'
import { showToast } from 'vant'
import type { Note, NotePriority, NoteStatus } from '@/types/handbook'
import TagSelector from './TagSelector.vue'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()
const noteEditorStore = useNoteEditorStore()

const noteId = route.params.id as string
const handbookId = route.query.handbook as string
const isNew = route.fullPath.includes('/new')

// 从 store 中获取数据
const title = ref(noteEditorStore.draftTitle || '')
const content = ref(noteEditorStore.draftContent || '')
const messageIds = ref(noteEditorStore.draftMessageIds || [])

// 在组件卸载时清除草稿数据
onUnmounted(() => {
  noteEditorStore.clearDraft()
})

// 表单数据

const selectedTags = ref<string[]>([])
const priority = ref<NotePriority>('medium')
const status = ref<NoteStatus>('待复习')
const canShare = ref(true)
const newTagName = ref('')

// 文件上传
const fileList = ref<any[]>([])
const isUploading = ref(false)

onMounted(async () => {
  await store.fetchTags()
  if (!isNew) {
    await loadNote()
  } else {
    // 新建笔记时默认设置为待复习
    status.value = '待复习'
    canShare.value = true
  }
})

// 加载笔记数据
async function loadNote() {
  try {
    const note = await store.fetchNote(Number(noteId))
    title.value = note.title
    content.value = note.content
    selectedTags.value = note.tags.map(tag => tag.name)
    priority.value = note.priority
    status.value = note.status
    canShare.value = note.is_shared
    // 加载附件列表
    fileList.value = note.attachments.map(attachment => ({
      url: attachment.file_path,
      name: attachment.original_name,
      isImage: attachment.mime_type.startsWith('image/')
    }))
  } catch (error) {
    showToast('加载笔记失败')
    // router.back()
  }
}

// 添加新标签
async function handleAddTag() {
  if (!newTagName.value) return
  
  if (!selectedTags.value.includes(newTagName.value)) {
    selectedTags.value.push(newTagName.value)
  }
  newTagName.value = ''
}

// 文件上传
async function handleUpload(file: File) {
  try {
    isUploading.value = true
    // TODO: 实现文件上传逻辑
    fileList.value.push({
      url: URL.createObjectURL(file),
      name: file.name,
      isImage: file.type.startsWith('image/')
    })
    return true
  } catch (error) {
    showToast('文件上传失败')
    return false
  } finally {
    isUploading.value = false
  }
}

// 删除文件
async function handleDeleteFile(file: any) {
  // TODO: 实现文件删除逻辑
  const index = fileList.value.indexOf(file)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 保存笔记
async function handleSave() {
  try {
    if (!title.value || !content.value) {
      showToast('请填写标题和内容')
      return
    }

    const data = {
      title: title.value,
      content: content.value,
      handbook_id: Number(handbookId),
      tags: selectedTags.value,
      priority: priority.value,
      status: status.value,
      is_shared: canShare.value,
      message_ids: messageIds.value,
      attachments: fileList.value.map(file => ({
        url: file.url,
        file_name: file.name
      }))
    }

    if (isNew) {
      await store.createNote(data)
    } else {
      await store.updateNote(Number(noteId), data)
    }

    showToast('保存成功')
    router.back()
  } catch (error) {
    showToast('保存失败')
  }
}
</script>

<template>
  <div class="note-editor">
    <!-- 工具栏 -->
    <van-nav-bar
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <van-button 
          type="primary" 
          size="small"
          :loading="store.isLoading"
          @click="handleSave"
        >
          保存
        </van-button>
      </template>
    </van-nav-bar>

    <!-- 编辑区域 -->
    <div class="editor-content">
      <!-- 标题 -->
      <van-field
        v-model="title"
        label="标题"
        placeholder="请输入笔记标题"
        required
      />

      <!-- 内容 -->
      <van-field
        v-model="content"
        type="textarea"
        label="内容"
        placeholder="请输入笔记内容"
        rows="6"
        required
      />

      <!-- 标签 -->
      <div class="tag-section">
        <div class="section-title">标签</div>
        <TagSelector
          v-model="selectedTags"
          :max-tags="5"
        />
      </div>

      <!-- 优先级和状态 -->
      <van-cell-group>
        <van-field
          label="优先级"
          readonly
        >
          <template #input>
            <van-radio-group v-model="priority" direction="horizontal">
              <van-radio name="low">低</van-radio>
              <van-radio name="medium">中</van-radio>
              <van-radio name="high">高</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <van-field
          label="状态"
          readonly
        >
          <template #input>
            <div class="status-cell">
              <span :class="['status-text', `status-${status}`]">{{ status }}</span>
            </div>
          </template>
        </van-field>
      </van-cell-group>

      <!-- 附件 -->
      <div class="attachments">
        <div class="section-title">附件</div>
        <van-uploader
          v-model="fileList"
          :max-count="5"
          :before-read="handleUpload"
          :loading="isUploading"
        />
        <div class="attachment-list">
          <van-cell
            v-for="file in fileList"
            :key="file.url"
            :title="file.name"
          >
            <template #right-icon>
              <van-button 
                size="small"
                icon="delete"
                @click="handleDeleteFile(file)"
              />
            </template>
          </van-cell>
        </div>
      </div>

      <!-- 分享设置 -->
      <van-cell-group>
        <van-cell title="是否能进行分享">
          <template #right-icon>
            <van-switch v-model="canShare" />
          </template>
        </van-cell>
      </van-cell-group>
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

  .tag-section {
    margin: var(--van-padding-md) 0;
    
    .section-title {
      margin-bottom: var(--van-padding-xs);
      font-weight: 500;
    }
  }

  .attachments {
    margin: var(--van-padding-md) 0;
    
    .section-title {
      margin-bottom: var(--van-padding-xs);
      font-weight: 500;
    }
    
    .attachment-list {
      margin-top: var(--van-padding-md);
    }
  }

  .status-text {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 14px;
    
    &.status-待复习 {
      background-color: #fef0f0;
      color: #f56c6c;
    }
    
    &.status-复习中 {
      background-color: #e6f7ff;
      color: #1890ff;
    }
    
    &.status-已完成 {
      background-color: #f6ffed;
      color: #52c41a;
    }
  }

  .status-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .status-label {
      white-space: nowrap;
    }

    .status-text {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 14px;
      
      &.status-待复习 {
        background-color: #fef0f0;
        color: #f56c6c;
      }
      
      &.status-复习中 {
        background-color: #e6f7ff;
        color: #1890ff;
      }
      
      &.status-已完成 {
        background-color: #f6ffed;
        color: #52c41a;
      }
    }
  }
}
</style> 