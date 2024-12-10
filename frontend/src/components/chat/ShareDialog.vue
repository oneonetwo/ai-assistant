<script setup lang="ts">
import { computed, ref } from 'vue'
import QRCode from 'qrcode'
import { useClipboard } from '@vueuse/core'
import { watch } from 'vue';

const props = defineProps<{
  show: boolean
  messages: Message[]
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>()

const { copy } = useClipboard()
const qrCodeUrl = ref('')
const shareLink = computed(() => {
  const baseUrl = window.location.origin
  const data = encodeURIComponent(JSON.stringify(props.messages))
  return `${baseUrl}/share?data=${data}`
})

watch(() => props.show, async (show) => {
  if (show) {
    try {
      qrCodeUrl.value = await QRCode.toDataURL(shareLink.value)
    } catch (error) {
      console.error('生成二维码失败:', error)
    }
  }
})

async function handleCopyLink() {
  await copy(shareLink.value)
  showToast('链接已复制')
}

function handleDownload() {
  const element = document.createElement('a')
  element.setAttribute('href', qrCodeUrl.value)
  element.setAttribute('download', 'share-qr.png')
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}
</script>

<template>
  <van-dialog
    :show="show"
    title="分享对话"
    class="share-dialog"
  >
    <div class="share-content">
      <div class="qr-code">
        <img 
          v-if="qrCodeUrl"
          :src="qrCodeUrl"
          alt="分享二维码"
        />
      </div>
      
      <div class="share-actions">
        <van-button
          block
          type="primary"
          @click="handleCopyLink"
        >
          复制链接
        </van-button>
        
        <van-button
          block
          plain
          @click="handleDownload"
        >
          下载二维码
        </van-button>
      </div>
    </div>
  </van-dialog>
</template>

<style lang="scss" scoped>
.share-content {
  padding: var(--van-padding-md);
}

.qr-code {
  display: flex;
  justify-content: center;
  margin-bottom: var(--van-padding-md);
  
  img {
    width: 200px;
    height: 200px;
  }
}

.share-actions {
  display: flex;
  flex-direction: column;
  gap: var(--van-padding-xs);
}
</style> 