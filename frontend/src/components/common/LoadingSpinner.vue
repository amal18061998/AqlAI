<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div
      class="rounded-full border-2 border-current border-t-transparent animate-spin"
      :class="sizeClasses"
    ></div>
    <span v-if="text" class="ml-2 text-sm text-stone-500">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: { type: String, default: 'md' },  // sm, md, lg
  text: { type: String, default: '' },
  containerClass: { type: String, default: '' },
})

const sizeClasses = computed(() => ({
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-10 h-10',
}[props.size]))
</script>
