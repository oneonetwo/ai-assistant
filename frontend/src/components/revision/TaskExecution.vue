<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { RevisionTask } from '@/types/revision'
import MarkdownIt from 'markdown-it'
import { useTimeSpent } from '@/composables/useTimeSpent'

const router = useRouter()

const props = defineProps<{
  task: RevisionTask
  mode?: 'normal' | 'quick'
}>()

const emit = defineEmits<{
  (e: 'complete', data: {
    taskId: number
    masteryLevel: RevisionTask['mastery_level']
    timeSpent: number
  }): void
}>()

const showContent = ref(false)
const md = new MarkdownIt()

const renderedContent = computed(() => {
  return md.render(props.task.note.content)
})

const masteryColor = computed(() => {
  switch (props.task.mastery_level) {
    case 'mastered':
      return 'success'
    case 'partially_mastered':
      return 'warning'
    case 'not_mastered':
      return 'danger'
    default:
      return 'default'
  }
})

const { timeSpent, startTimer, stopTimer } = useTimeSpent()

function handleMasteryChange(masteryLevel: RevisionTask['mastery_level']) {
  stopTimer()
  emit('complete', {
    taskId: props.task.id,
    masteryLevel,
    timeSpent: timeSpent.value
  })
}

watch(showContent, (newValue) => {
  if (newValue) {
    startTimer()
  }
})

function handleTitleClick(event: Event) {
  event.stopPropagation()
  router.push({
    name: 'note-detail',
    params: { id: props.task.note.id }
  })
}
</script>

<template>
  <div class="task-execution">
    <div class="task-header">
      <div class="title-wrapper">
        <h3 @click="handleTitleClick">{{ task.note.title }}</h3>
        <van-icon name="arrow" class="title-icon" />
      </div>
      <van-tag :type="masteryColor" round>
        {{ task.mastery_level === 'mastered' ? '已熟记' :
           task.mastery_level === 'partially_mastered' ? '部分掌握' :
           task.mastery_level === 'not_mastered' ? '记不清' : '待评估' }}
      </van-tag>
    </div>

    <div class="task-meta">
      <van-tag plain type="primary">复习次数: {{ task.revision_count }}</van-tag>
      <van-tag plain :type="task.note.priority === 'high' ? 'danger' : 
                            task.note.priority === 'medium' ? 'warning' : 'primary'">
        {{ task.note.priority === 'high' ? '高优先级' :
           task.note.priority === 'medium' ? '中优先级' : '低优先级' }}
      </van-tag>
    </div>

    <div class="task-actions">
      <van-button 
        block 
        :type="showContent ? 'default' : 'primary'"
        @click="showContent = !showContent"
      >
        {{ showContent ? '隐藏内容' : '查看内容' }}
      </van-button>
    </div>

    <div v-show="showContent" class="task-content">
      <div class="markdown-body" v-html="renderedContent" />
    </div>

    <div class="status-buttons">
      <div class="button-group">
        <van-button 
          :type="task.mastery_level === 'not_mastered' ? 'danger' : 'default'"
          @click="handleMasteryChange('not_mastered')"
        >
          记不清
        </van-button>
        <van-button 
          :type="task.mastery_level === 'partially_mastered' ? 'warning' : 'default'"
          @click="handleMasteryChange('partially_mastered')"
        >
          部分掌握
        </van-button>
        <van-button 
          :type="task.mastery_level === 'mastered' ? 'success' : 'default'"
          @click="handleMasteryChange('mastered')"
        >
          已熟记，跳过
        </van-button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.task-execution {
  padding: 16px;

  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .title-wrapper {
      display: flex;
      align-items: center;
      gap: 4px;
      
      h3 {
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        color: var(--van-primary-color);
        
        &:hover {
          opacity: 0.8;
          text-decoration: underline;
        }
      }

      .title-icon {
        font-size: 14px;
        color: var(--van-gray-5);
      }
    }
  }

  .task-meta {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }

  .task-actions {
    margin-bottom: 16px;
  }

  .task-content {
    margin-bottom: 16px;
    padding: 16px;
    background: var(--van-background-2);
    border-radius: 8px;
  }

  .status-buttons {
    padding: 16px;
    
    .button-group {
      display: flex;
      gap: 8px;
      
      .van-button {
        flex: 1;
      }
    }
  }
}
</style> 