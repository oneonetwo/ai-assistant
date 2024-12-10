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

    <div v-if="mode !== 'quick'" class="mastery-controls">
      <van-button 
        type="danger" 
        @click="handleMasteryChange('not_mastered')"
      >
        不熟悉
      </van-button>
      <van-button 
        type="warning" 
        @click="handleMasteryChange('partially_mastered')"
      >
        学习中
      </van-button>
      <van-button 
        type="success" 
        @click="handleMasteryChange('mastered')"
      >
        已掌握
      </van-button>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.task-execution {
  padding: 16px;
  background-color: var(--van-background);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to right, rgba(0, 0, 0, 0.03) 0px, transparent 1px) 0 0;
    background-size: 20px 100%;
    pointer-events: none;
  }

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

    .van-tag {
      padding: 4px 8px;
      font-size: 12px;
      font-weight: 500;
      border-radius: 6px;
      margin-right: 8px;
      transition: all 0.3s ease;

      &--primary {
        background: var(--van-primary-color);
        color: white;
        border: none;
      }

      &--success {
        background: rgba(var(--van-success-color), 0.1);
        color: var(--van-success-color);
        border: 1px solid var(--van-success-color);
      }

      &--warning {
        background: rgba(var(--van-warning-color), 0.1);
        color: var(--van-warning-color);
        border: 1px solid var(--van-warning-color);
      }

      &--danger {
        background: rgba(var(--van-danger-color), 0.1);
        color: var(--van-danger-color);
        border: 1px solid var(--van-danger-color);
      }
    }
  }

  .task-actions {
    margin-bottom: 16px;

    .van-button {
      height: 40px;
      font-size: 14px;
      font-weight: 500;
      border-radius: 8px;
      margin: 0 8px;
      transition: all 0.3s ease;

      &--view {
        background: var(--van-primary-color);
        border-color: var(--van-primary-color);
        color: white;

        &:active {
          opacity: 0.8;
        }
      }
    }
  }

  .task-content {
    margin-bottom: 16px;
    padding: 16px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(230, 230, 250, 0.8)); // 更加鲜明的渐变效果
    border-radius: 8px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;

    &:hover {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(210, 210, 240, 0.9)); // 悬停时的渐变变化
    }
  }

  .mastery-controls {
    margin-top: var(--van-padding-md);
    display: flex;
    gap: var(--van-padding-xs);
    justify-content: center;

    .van-button {
      &--not-mastered {
        background: rgba(var(--van-danger-color), 0.1);
        border-color: var(--van-danger-color);
        color: var(--van-danger-color);

        &:active {
          background: rgba(var(--van-danger-color), 0.2);
        }
      }

      &--learning {
        background: rgba(var(--van-warning-color), 0.1);
        border-color: var(--van-warning-color);
        color: var(--van-warning-color);

        &:active {
          background: rgba(var(--van-warning-color), 0.2);
        }
      }

      &--mastered {
        background: rgba(var(--van-success-color), 0.1);
        border-color: var(--van-success-color);
        color: var(--van-success-color);

        &:active {
          background: rgba(var(--van-success-color), 0.2);
        }
      }
    }
  }
}

// 深色主题
:root[data-theme="dark"] {
  .task-execution {
    background: rgba(70, 80, 95, 0.6);
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);

    &::before {
      background: linear-gradient(to right, rgba(255, 255, 255, 0.03) 0px, transparent 1px) 0 0;
    }

    .task-content {
      background: linear-gradient(135deg, rgba(60, 60, 60, 0.8), rgba(40, 40, 60, 0.8)); // 深色主题下的渐变效果
      backdrop-filter: blur(4px);
    }
  }
}

// 浅色主题
:root[data-theme="light"] {
  .task-execution {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);

    &:hover {
      background: rgba(255, 255, 255, 0.95);
    }

    &::before {
      background: linear-gradient(to right, rgba(0, 0, 0, 0.03) 0px, transparent 1px) 0 0;
    }

    .task-content {
      background: linear-gradient(135deg, rgba(250, 250, 250, 0.8), rgba(230, 230, 250, 0.8)); // 浅色主题下的渐变效果
      backdrop-filter: blur(8px);
      border: 1px solid rgba(0, 0, 0, 0.05);

      &:hover {
        background: linear-gradient(135deg, rgba(252, 252, 252, 0.9), rgba(210, 210, 240, 0.9)); // 悬停时的渐变变化
      }
    }
  }
}

.task-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  .van-tag {
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    border-radius: 16px;
    margin-right: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(4px);
    border: none;

    &--plain {
      background: rgba(var(--van-primary-color), 0.08);
      color: var(--van-primary-color);

      &:hover {
        background: rgba(var(--van-primary-color), 0.12);
      }
    }

    // 复习次数标签
    &--primary {
      background: linear-gradient(135deg, rgba(var(--van-primary-color), 0.1), rgba(var(--van-primary-color), 0.2));
      color: var(--van-primary-color);
    }

    // 优先级标签
    &--danger {
      background: linear-gradient(135deg, rgba(var(--van-danger-color), 0.1), rgba(var(--van-danger-color), 0.2));
      color: var(--van-danger-color);
    }

    &--warning {
      background: linear-gradient(135deg, rgba(var(--van-warning-color), 0.1), rgba(var(--van-warning-color), 0.2));
      color: var(--van-warning-color);
    }

    // 掌握程度标签
    &--success {
      background: linear-gradient(135deg, rgba(var(--van-success-color), 0.1), rgba(var(--van-success-color), 0.2));
      color: var(--van-success-color);
    }
  }
}

.task-actions {
  margin-bottom: 16px;

  .van-button {
    height: 44px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 22px;
    margin: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(4px);
    border: none;
    background: linear-gradient(135deg, rgba(var(--van-primary-color), 0.1), rgba(var(--van-primary-color), 0.2));
    color: var(--van-primary-color);
    
    &:active {
      transform: scale(0.98);
    }

    &:hover {
      background: linear-gradient(135deg, rgba(var(--van-primary-color), 0.15), rgba(var(--van-primary-color), 0.25));
    }
  }
}

.mastery-controls {
  margin-top: var(--van-padding-md);
  display: flex;
  gap: 12px;
  justify-content: center;

  .van-button {
    flex: 1;
    max-width: 120px;
    height: 44px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 22px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(4px);
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    &:active {
      transform: scale(0.98);
    }

    // 不熟悉按钮
    &[type="danger"] {
      background: linear-gradient(135deg, rgba(var(--van-danger-color), 0.1), rgba(var(--van-danger-color), 0.2));
      color: var(--van-danger-color);

      &:hover {
        background: linear-gradient(135deg, rgba(var(--van-danger-color), 0.15), rgba(var(--van-danger-color), 0.25));
      }
    }

    // 学习中按钮
    &[type="warning"] {
      background: linear-gradient(135deg, rgba(var(--van-warning-color), 0.1), rgba(var(--van-warning-color), 0.2));
      color: var(--van-warning-color);

      &:hover {
        background: linear-gradient(135deg, rgba(var(--van-warning-color), 0.15), rgba(var(--van-warning-color), 0.25));
      }
    }

    // 已掌握按钮
    &[type="success"] {
      background: linear-gradient(135deg, rgba(var(--van-success-color), 0.1), rgba(var(--van-success-color), 0.2));
      color: var(--van-success-color);

      &:hover {
        background: linear-gradient(135deg, rgba(var(--van-success-color), 0.15), rgba(var(--van-success-color), 0.25));
      }
    }
  }
}

// 深色主题调整
:root[data-theme="dark"] {
  .task-execution {
    .van-tag {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }

    .van-button {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
  }
}

// 浅色主题调整
:root[data-theme="light"] {
  .task-execution {
    .van-tag {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    }

    .van-button {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
  }
}
</style>