<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useElementHover } from '@vueuse/core'

const props = defineProps<{
  content: string
}>()

const previewRef = ref<HTMLElement>()
const isHovered = useElementHover(previewRef)

const previewContent = computed(() => {
  const maxLength = 200
  const content = props.content.length > maxLength
    ? props.content.slice(0, maxLength) + '...'
    : props.content
  return marked(content)
})
</script>

<template>
  <div 
    ref="previewRef"
    class="message-preview"
    :class="{ 'is-expanded': isHovered }"
  >
    <div 
      class="preview-content markdown-body"
      v-html="previewContent"
    />
    
    <div v-if="content.length > 200" class="preview-fade" />
  </div>
</template>

<style lang="scss" scoped>
.message-preview {
  position: relative;
  max-height: 100px;
  overflow: hidden;
  border-radius: var(--van-radius-md);
  background: var(--van-background-2);
  transition: max-height 0.3s ease;
  
  &.is-expanded {
    max-height: 300px;
    
    .preview-fade {
      opacity: 0;
    }
  }
}

.preview-content {
  padding: var(--van-padding-sm);
  font-size: 14px;
}

.preview-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--van-background-2)
  );
  transition: opacity 0.3s ease;
}
</style> 