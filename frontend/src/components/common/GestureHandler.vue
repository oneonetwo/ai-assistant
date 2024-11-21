<script setup lang="ts">
import { ref } from 'vue'
import { useEventListener } from '@vueuse/core'

const startX = ref(0)
const startY = ref(0)
const isDragging = ref(false)

const props = defineProps<{
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  threshold?: number
}>()

const threshold = props.threshold || 50

useEventListener(window, 'touchstart', (e: TouchEvent) => {
  startX.value = e.touches[0].clientX
  startY.value = e.touches[0].clientY
  isDragging.value = true
})

useEventListener(window, 'touchmove', (e: TouchEvent) => {
  if (!isDragging.value) return

  const deltaX = e.touches[0].clientX - startX.value
  const deltaY = e.touches[0].clientY - startY.value

  // 确保横向滑动
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    e.preventDefault()
  }
})

useEventListener(window, 'touchend', (e: TouchEvent) => {
  if (!isDragging.value) return

  const deltaX = e.changedTouches[0].clientX - startX.value
  const deltaY = e.changedTouches[0].clientY - startY.value

  if (Math.abs(deltaX) > threshold && Math.abs(deltaX) > Math.abs(deltaY)) {
    if (deltaX > 0 && props.onSwipeRight) {
      props.onSwipeRight()
    } else if (deltaX < 0 && props.onSwipeLeft) {
      props.onSwipeLeft()
    }
  }

  isDragging.value = false
})
</script>

<template>
  <slot />
</template> 