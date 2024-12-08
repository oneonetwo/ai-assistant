<script setup lang="ts">
import { ref } from 'vue'
import { Picker, showToast } from 'vant'

const props = withDefaults(defineProps<{
  modelValue: string
}>(), {
  modelValue: '09:00'
})
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const columns = Array.from({ length: 24 }, (_, hour) => 
  Array.from({ length: 60 }, (_, minute) => ({
    text: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`,
    value: `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
  }))
).flat()

const showPicker = ref(false)
const pickerValue = ref([
  props.modelValue,
  columns.findIndex(item => item.value === props.modelValue)
])



function onConfirm({ selectedOptions, selectedValues }: { selectedOptions: { text: string; value: string }[]; selectedValues: string[] }) {
  console.log('onConfirm', selectedOptions, selectedValues)
  showPicker.value = false
  pickerValue.value = selectedValues
  emit('update:modelValue', selectedOptions[0].value)
}
</script>

<template>
  <div class="time-picker-field">
    <van-field
      readonly
      clickable
      :model-value="modelValue"
      label="提醒时间"
      placeholder="请选择提醒时间"
      @click="showPicker = true"
    />
    
    <van-popup
      v-model:show="showPicker"
      position="bottom"
      round
      destroy-on-close
    >
      <van-picker
        :columns="columns"
        :model-value="pickerValue"
        :default-index="columns.findIndex(item => item.value === modelValue)"
        @confirm="onConfirm"
        @cancel="showPicker = false"
        class="dark-theme-picker"
      />
    </van-popup>
  </div>
</template> 

<style lang="scss" scoped>
.dark-theme-picker {
  :deep {
    .van-picker {
      background-color: var(--van-background-2);
      color: var(--van-text-color);
    }

    .van-picker__toolbar {
      background-color: var(--van-background-2);
      border-bottom: 1px solid var(--van-border-color);
      
      .van-picker__cancel,
      .van-picker__confirm {
        color: var(--van-primary-color);
        
        &:active {
          opacity: 0.7;
        }
      }
    }

    .van-picker-column__wrapper {
      background-color: var(--van-background-2);
    }

    .van-picker-column {
      background-color: var(--van-background-2);
      
      &::before {
        background: linear-gradient(180deg, 
          var(--van-background-2) 0%,
          rgba(var(--van-background-2-rgb), 0.1) 100%
        );
      }

      &::after {
        background: linear-gradient(0deg, 
          var(--van-background-2) 0%,
          rgba(var(--van-background-2-rgb), 0.1) 100%
        );
      }
    }

    .van-picker-column__item {
      color: var(--van-text-color-2);

      &--selected {
        color: var(--van-text-color);
        font-weight: 600;
      }
    }
  }
}
</style>