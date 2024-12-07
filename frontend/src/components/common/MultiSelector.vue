<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'

interface Option {
  text: string
  value: number | string
}

const props = defineProps<{
  modelValue: (number | string)[]
  options: Option[]
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: (number | string)[]): void
}>()

const isOpen = ref(false)

const selectedText = computed(() => {
  if (!props.modelValue?.length) return props.placeholder
  return props.modelValue
    .map(value => props.options.find(opt => opt.value === value)?.text)
    .filter(Boolean)
    .join(', ')
})

function handleOptionClick(value: number | string) {
  const newValue = [...(props.modelValue || [])]
  const index = newValue.indexOf(value)
  
  if (index === -1) {
    newValue.push(value)
  } else {
    newValue.splice(index, 1)
  }
  
  emit('update:modelValue', newValue)
}

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
  <div class="multi-selector" ref="selectorRef" @click.stop="isOpen = !isOpen">
    <div class="selector-header">
      <span :class="{ placeholder: !modelValue?.length }">{{ selectedText }}</span>
      <van-icon :name="isOpen ? 'arrow-up' : 'arrow-down'" />
    </div>
    
    <div v-show="isOpen" class="options-container">
      <div
        v-for="option in options"
        :key="option.value"
        class="option-item"
        :class="{ active: modelValue?.includes(option.value) }"
        @click.stop="handleOptionClick(option.value)"
      >
        <van-checkbox :modelValue="modelValue?.includes(option.value)">
          {{ option.text }}
        </van-checkbox>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.multi-selector {
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
  }
  
  .option-item {
    display: flex;
    align-items: center;
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
    
    :deep(.van-checkbox) {
      width: 100%;
    }
  }
}
</style>