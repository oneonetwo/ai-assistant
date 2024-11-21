<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import { exportToPDF } from '@/utils/pdf-export'

const route = useRoute()
const router = useRouter()
const messages = ref<Message[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const shareId = route.params.id as string
    // 这里应该调用 API 获取分享的消息
    const response = await fetch(`/api/share/${shareId}`)
    if (!response.ok) {
      throw new Error('获取分享内容失败')
    }
    messages.value = await response.json()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    showToast({
      message: error.value,
      type: 'fail'
    })
  } finally {
    isLoading.value = false
  }
})

async function handleExport() {
  try {
    await exportToPDF(messages.value, {
      title: '分享的对话',
      author: '来自 AI 助手'
    })
  } catch (error) {
    showToast('导出失败')
  }
}

function handleCopy() {
  const url = window.location.href
  navigator.clipboard.writeText(url)
    .then(() => showToast('链接已复制'))
    .catch(() => showToast('复制失败'))
}
</script>

<template>
  <div class="share-view">
    <van-nav-bar
      title="分享的对话"
      left-arrow
      @click-left="router.back()"
    >
      <template #right>
        <van-dropdown-menu>
          <van-dropdown-item>
            <van-cell-group>
              <van-cell 
                title="导出 PDF" 
                icon="description"
                @click="handleExport"
              />
              <van-cell 
                title="复制链接" 
                icon="link"
                @click="handleCopy"
              />
            </van-cell-group>
          </van-dropdown-item>
        </van-dropdown-menu>
      </template>
    </van-nav-bar>

    <div class="message-container">
      <template v-if="isLoading">
        <van-skeleton title avatar row="3" />
      </template>
      
      <template v-else-if="error">
        <van-empty
          :description="error"
          image="error"
        >
          <template #bottom>
            <van-button 
              round 
              type="primary"
              @click="router.push('/')"
            >
              返回首页
            </van-button>
          </template>
        </van-empty>
      </template>
      
      <template v-else>
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
          readonly
        />
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.share-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--van-padding-sm);
}
</style> 