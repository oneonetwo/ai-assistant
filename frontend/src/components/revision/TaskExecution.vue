<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RevisionTask } from '@/types/revision'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  task: RevisionTask
}>()

const emit = defineEmits<{
  (e: 'status-change', taskId: number, status: RevisionTask['status'], masteryLevel: RevisionTask['mastery_level']): void
}>()

const showContent = ref(false)
const md = new MarkdownIt()

const renderedContent = computed(() => {
  return md.render(props.task.note.content)
})

const masteryColor = computed(() => {
  switch (props.task.mastery_level) {
    case 'fully_mastered':
      return 'success'
    case 'partially_mastered':
      return 'warning'
    case 'not_mastered':
      return 'danger'
    default:
      return 'default'
  }
})

function handleMasteryChange(masteryLevel: RevisionTask['mastery_level']) {
  emit('status-change', props.task, masteryLevel)
}
</script>

<template>
  <div class="task-execution">
    <div class="task-header">
      <h3>{{ task.note.title }}</h3>
      <van-tag :type="masteryColor" round>
        {{ task.mastery_level === 'fully_mastered' ? '完全掌握' :
           task.mastery_level === 'partially_mastered' ? '部分掌握' :
           task.mastery_level === 'not_mastered' ? '未掌握' : '待评估' }}
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
          跳过
        </van-button>
        <van-button 
          :type="task.mastery_level === 'partially_mastered' ? 'warning' : 'default'"
          @click="handleMasteryChange('partially_mastered')"
        >
          记不清
        </van-button>
        <van-button 
          :type="task.mastery_level === 'fully_mastered' ? 'success' : 'default'"
          @click="handleMasteryChange('fully_mastered')"
        >
          记住了
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

    h3 {
      font-size: 16px;
      font-weight: 500;
    }
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