<script setup lang="ts">
import { ref, computed, onMounted, watchEffect, nextTick } from 'vue'
import { useElementSize, useScroll } from '@vueuse/core'

interface Props {
  data: any[]
  itemHeight: number
  buffer?: number
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  buffer: 5
})

const containerRef = ref<HTMLElement>()
const { height: containerHeight } = useElementSize(containerRef)
const { y: scrollTop } = useScroll(containerRef)

// 计算可见区域的起始和结束索引
const visibleRange = computed(() => {
  const height = containerHeight.value || 0
  const visibleCount = Math.ceil(height / props.itemHeight)
  
  let start = Math.floor((scrollTop.value || 0) / props.itemHeight) - props.buffer
  let end = start + visibleCount + 2 * props.buffer
  
  // 边界处理
  start = Math.max(0, start)
  end = Math.min(props.data.length || 0, end)
  
  return { start, end }
})

// 计算可见项目
const visibleItems = computed(() => {
  if (!props.data?.length) return []
  
  const { start, end } = visibleRange.value
  return props.data.slice(start, end).map((item, index) => ({
    item,
    style: {
      position: 'absolute',
      top: `${(start + index) * props.itemHeight}px`,
      width: '100%',
      height: `${props.itemHeight}px`
    }
  }))
})

// 计算总高度
const totalHeight = computed(() => {
  return (props.data?.length || 0) * props.itemHeight
})

// 监听数据变化，自动滚动到底部
watchEffect(() => {
  if (props.data?.length) {
    nextTick(() => {
      containerRef.value?.scrollTo({
        top: totalHeight.value,
        behavior: 'smooth'
      })
    })
  }
})
</script>

<template>
  <div 
    ref="containerRef"
    class="virtual-list"
  >
    <div 
      class="virtual-list-phantom"
      :style="{ height: `${totalHeight}px` }"
    />
    <div class="virtual-list-content">
      <template v-for="{ item, style } in visibleItems" :key="item.id">
        <slot
          :item="item"
          :style="style"
        />
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.virtual-list {
  position: relative;
  overflow-y: auto;
  height: 100%;
}

.virtual-list-phantom {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  z-index: -1;
}

.virtual-list-content {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
}
</style> 