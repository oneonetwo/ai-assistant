<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHandbookStore } from '@/stores/handbook'
import { useNoteEditorStore } from '@/stores/noteEditor'
import { useRevisionStore } from '@/stores/revision'
import { showToast } from 'vant'
import type { Note, NotePriority, NoteStatus } from '@/types/handbook'
import TagSelector from './TagSelector.vue'
import MultiSelector from '@/components/common/MultiSelector.vue'
import { uploadToOSS } from '@/utils/oss'

const route = useRoute()
const router = useRouter()
const store = useHandbookStore()
const noteEditorStore = useNoteEditorStore()
const revisionStore = useRevisionStore()

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

// 文件类型映射
const FILE_TYPES = {
  IMAGE: [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/bmp'
  ],
  DOCUMENT: [
    'text/plain',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/msword',
    'application/vnd.ms-excel',
    'application/vnd.ms-powerpoint',
    'text/markdown',
    'application/json',
    'text/x-markdown'
  ],
  AUDIO: [
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/x-m4a',
    'audio/aac'
  ]
} as const

// 文件上传
const fileList = ref<any[]>([])
const isUploading = ref(false)
const uploadProgress = ref(0)

const hasRevisionPlans = ref(false)

const selectedPlanIds = ref<number[]>([])
const planOptions = ref<{ text: string; value: number }[]>([])

onMounted(async () => {
  await store.fetchTags()
  console.log('isNew', isNew)
  if (!isNew) {
    await loadNote()
  } else {
    // 查询是否有复习计划
    const result = await revisionStore.checkHandbookPlans(Number(handbookId))
    const plans = result.plans
    hasRevisionPlans.value = plans.length > 0
    // 转换计划数据为 Selector 需要的格式
    planOptions.value = plans.map(plan => ({
      text: plan.name,
      value: plan.id
    }))
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
    // 统一附件列表格式
    fileList.value = note.attachments.map(attachment => ({
      original_name: attachment.original_name,
      file_type: attachment.file_type,
      file_size: attachment.file_size,
      file_path: attachment.file_path
    }))
  } catch (error) {
    showToast('加载笔记失败')
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
    console.log('file', file)
    // 创建临时预览URL
    const tempUrl = URL.createObjectURL(file)
    
    // 添加到文件列表，先用临时URL
    const fileInfo = {
      original_name: file.name,
      file_type: file.type,
      file_size: file.size,
      file_path: tempUrl
    }
    // 上传到OSS
    const ossUrl = await uploadToOSS(file, {
      onProgress: (progress) => {
        uploadProgress.value = progress
      }
    })
    // 上传成功后更新文件路径
    fileInfo.file_path = ossUrl
    console.log('fileInfo', fileInfo)
    fileList.value.push(fileInfo)
    console.log('fileList', fileList.value)

    return true
  } catch (error) {
    showToast('文件上传失败')
    return false
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
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
      // 统一附件数据结构
      attachments: fileList.value.map(file => ({
        original_name: file.original_name,
        file_type: file.file_type,
        file_size: file.file_size,
        file_path: file.file_path
      }))
    }

    let newNoteId: number
    if (isNew) {
      const result = await store.createNote(data)
      newNoteId = result.id
      
      // 如果选择了复习计划,批量添加
      if (selectedPlanIds.value.length > 0) {
        await revisionStore.addNoteToPlansBatch({
          note_id: newNoteId,
          plan_ids: selectedPlanIds.value,
          start_date: new Date().toISOString(),
          priority: 3
        })
      }
    } else {
      await store.updateNote(Number(noteId), data)
    }

    showToast('保存成功')
    router.push(`/handbooks/${handbookId}`)
  } catch (error) {
    console.error(error)
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
      <div class="tag-section" v-if="hasRevisionPlans && isNew">
        <div class="selector-wrapper">
          <MultiSelector
            v-model="selectedPlanIds"
            :options="planOptions"
            placeholder="请选择复习计划"
          />
        </div>
      </div>
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
      <!-- 分享设置 -->
      <van-cell-group>
        <van-cell title="是否能进行分享">
          <template #right-icon>
            <van-switch v-model="canShare" />
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 附件 -->
      <div class="attachments">
        <div class="section-title">附件</div>
        <van-uploader
          :file-list="fileList"
          :max-count="5"
          :before-read="handleUpload"
          :loading="isUploading"
          accept=".txt,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.epub,.md,.markdown,text/markdown,text/x-markdown,image/*,.mp3,.wav,.ogg,.m4a,.aac"
        >
          <template #preview-cover="{ file }">
            <div class="preview-info" v-if="file.file_path">
              <span class="file-name">{{ file.original_name }}</span>
              <span class="file-size">{{ (file.file_size / 1024).toFixed(1) }}KB</span>
              <van-progress 
                v-if="isUploading" 
                :percentage="uploadProgress" 
                :show-pivot="false"
              />
            </div>
          </template>
        </van-uploader>
        <div class="attachment-list">
          <van-cell
            v-for="file in fileList"
            :key="file.file_path"
            :title="file.original_name"
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
      <div class="tag-section"></div>
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

  .selector-wrapper {
    position: relative;
    width: 100%;
    z-index: 10;
  }
}

.preview-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 8px;
  color: white;
  font-size: 12px;

  .file-name {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-size {
    color: #ccc;
  }
}
</style> 