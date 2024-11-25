<script setup lang="ts">
import { ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import VoiceInput from './VoiceInput.vue'

const props = defineProps<{
  quotedMessage?: Message | null
}>()

const emit = defineEmits<{
  (e: 'quote-remove'): void
}>()

const messageText = ref('')
const chatStore = useChatStore()
const { isLoading } = storeToRefs(chatStore)

const featureTags = [
  { id: 1, icon: 'image', label: '创建图片' },
  { id: 2, icon: 'chart', label: '分析数据' },
  { id: 3, icon: 'doc', label: '总结文本' },
  { id: 4, icon: 'bulb', label: '构思' },
  { id: 5, icon: 'edit', label: '帮我写' },
  { id: 6, icon: 'calculator', label: '给我做算' },
  { id: 7, icon: 'analyze', label: '分析图片' },
  { id: 8, icon: 'code', label: '代码' }
]

// 处理标签点击
function handleTagClick(tag: typeof featureTags[0]) {
  messageText.value = `${tag.label}：\n`
}

// 处理语音输入
function handleVoiceInput(text: string) {
  messageText.value = text
}

// 处理发送消息
async function handleSend() {
  if (!messageText.value.trim()) return
  
  try {
    await chatStore.sendMessage(messageText.value, {
      quote: props.quotedMessage || undefined
    })
    messageText.value = ''
    emit('quote-remove')
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

// 移除引用
function removeQuote() {
  emit('quote-remove')
}

watch(() => chatStore.isLoading, (newVal) => {
  // 处理消息保存
  async function handleSave(content: string) {
    try {
      await chatStore.saveMessage(content)
    } catch (error) {
      showToast('保存失败')
    }
  }
})
</script>

<template>
  <div class="chat-input">
    <!-- 引用消息 -->
    <div v-if="quotedMessage" class="quoted-message">
      <div class="quote-content">
        <span class="quote-text">{{ quotedMessage.content }}</span>
        <van-icon name="cross" @click="removeQuote" />
      </div>
    </div>
    
    <div class="feature-tags">
      <div v-for="tag in featureTags" 
        :key="tag.id"
        class="tag"
        @click="handleTagClick(tag)"
      >
        <svg-icon :name="tag.icon" />
        <span>{{ tag.label }}</span>
      </div>
    </div>
    
    <div class="input-area">
      <van-field
        v-model="messageText"
        type="textarea"
        placeholder="输入消息，Shift + Enter 换行"
        rows="3"
        autosize
        @keydown.enter.prevent="handleSend"
        ref="inputRef"
      >
        <template #button>
          <van-button
            type="primary"
            :loading="isLoading"
            :disabled="!messageText.trim()"
            @click="handleSend"
          >
            发送
          </van-button>
        </template>
      </van-field>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.chat-input {
  padding: 16px;
  background: var(--van-background);
  border-top: 1px solid var(--van-border-color);

  .feature-tags {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    overflow-x: auto;
    padding-bottom: 8px;

    .tag {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      border-radius: 16px;
      background: var(--van-background-2);
      cursor: pointer;
      white-space: nowrap;
      transition: background 0.2s;

      &:hover {
        background: var(--van-active-color);
      }

      .svg-icon {
        width: 16px;
        height: 16px;
        color: var(--van-primary-color);
      }
    }
  }

  .input-area {
    position: relative;

    .action-buttons {
      display: flex;
      gap: 8px;
      margin-left: 8px;
    }
  }
}

.quoted-message {
  padding: 8px 12px;
  background: var(--van-background-2);
  border-bottom: 1px solid var(--van-border-color);
  
  .quote-content {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .quote-text {
      flex: 1;
      font-size: 14px;
      color: var(--van-text-color);
    }
  }
}
</style> 