<template>
  <van-image-preview
    class="file-preview"
    v-model:show="show"
    :images="[props.src]"
    :closeable="true"
    @close="handleClose"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  src: string
}>()

const show = ref(false)
const emit = defineEmits<{
  (e: 'close'): void
}>()

const handleClose = () => {
  show.value = false
  emit('close')
}

defineExpose({
  open: () => {
    show.value = true
  }
})
</script> 
<style lang="scss" scoped>

</style>