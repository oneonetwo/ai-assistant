<template>
  <div 
    class="message" 
    :class="[
      `message-${message.role}`,
      { 'message-sending': message.status === 'sending' }
    ]"
  >
    <div class="message-avatar">
      <van-image
        :src="message.role === 'user' ? '/avatar-user.png' : '/avatar-ai.png'"
        width="30"
        height="30"
        radius="4"
      />
    </div>

    <div class="message-wrapper">
      <!-- 引用消息 -->
      <MessageQuote 
        v-if="message.quote"
        :message="message.quote"
        class="message-quote"
      />

      <!-- 消息内容 -->
      <div class="message-bubble">
        <div 
          class="message-content markdown-body"
          v-html="formattedContent"
        />
        
        <!-- 消息状态 -->
        <div v-if="message.status" class="message-status">
          <van-loading v-if="message.status === 'sending'" size="16" />
          <van-icon 
            v-else-if="message.status === 'error'" 
            name="warning-o"
            class="error"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Message } from '@/types/chat'
import { marked } from 'marked'
import MessageQuote from './MessageQuote.vue'

const props = defineProps<{
  message: Message
}>()

// 格式化消息内容
const formattedContent = computed(() => {
  console.log('格式化消息内容', props.message)
  if (!props.message.content) return ''
  return marked(props.message.content, {
    breaks: true,
    gfm: true
  })
})
</script>
