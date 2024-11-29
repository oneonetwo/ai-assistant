<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'

interface Option {
  text: string
  value: number | string
}

const props = defineProps<{
  modelValue: number | string | undefined
  options: Option[]
  placeholder?: string
}>()
watch(() => props.modelValue, (newValue) => {
  console.log('newValue>>>>', newValue)
  if (newValue !== undefined) {
    isOpen.value = false
  }
})


const emit = defineEmits<{
  (e: 'update:modelValue', value: number | string): void
}>()

const isOpen = ref(false)

const selectedText = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)?.text || props.placeholder
})

const selectorRef = ref<HTMLElement>()

function handleClickOutside(event: MouseEvent) {
  if (selectorRef.value && !selectorRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="custom-selector" ref="selectorRef" @click="isOpen = !isOpen">
    <div class="selector-header">
      <span :class="{ placeholder: !modelValue }">{{ selectedText }}</span>
      <van-icon :name="isOpen ? 'arrow-up' : 'arrow-down'" />
    </div>
    
    <div v-show="isOpen" class="options-container">
      <div
        v-for="option in options"
        :key="option.value"
        class="option-item"
        :class="{ active: option.value === modelValue }"
        @click="emit('update:modelValue', option.value)"
      >
        {{ option.text }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.custom-selector {
  position: relative;
  width: 100%;
  
  .selector-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: var(--van-background);
    border: 1px solid var(--van-border-color);
    border-radius: 4px;
    cursor: pointer;
    
    .placeholder {
      color: var(--van-gray-5);
    }
    
    .van-icon {
      color: var(--van-gray-5);
    }
  }
  
  .options-container {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 100;
    margin-top: 4px;
    background: var(--van-background);
    border: 1px solid var(--van-border-color);
    border-radius: 4px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    max-height: 200px;
    overflow-y: auto;
    
    .option-item {
      padding: 10px 16px;
      cursor: pointer;
      transition: background-color 0.2s;
      
      &:hover {
        background: var(--van-background-2);
      }
      
      &.active {
        color: var(--van-primary-color);
        background: var(--van-background-2);
      }
    }
  }
}
</style>