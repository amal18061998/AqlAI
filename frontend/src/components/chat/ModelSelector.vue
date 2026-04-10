<template>
  <div class="relative" ref="dropdownRef">
    <button
      @click="toggleOpen"
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
             bg-stone-100 hover:bg-stone-200 text-stone-700 transition-colors cursor-pointer
             border border-stone-200"
    >
      {{ modelLabels[chatStore.selectedModel] }}
      <svg class="w-3.5 h-3.5 transition-transform" :class="{ 'rotate-180': open }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <Teleport to="body">
      <transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="open"
             :style="floatingStyle"
             class="fixed w-52 bg-white rounded-xl shadow-lg border border-stone-200 py-1 z-[9999]">
          <button
            v-for="(label, key) in modelLabels"
            :key="key"
            @click="selectModel(key)"
            class="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-stone-700
                   hover:bg-stone-50 transition-colors cursor-pointer text-start"
            :class="{ 'bg-indigo-50 text-indigo-700': chatStore.selectedModel === key }"
          >
            <span class="w-2 h-2 rounded-full" :class="modelColors[key]"></span>
            {{ label }}
            <svg v-if="chatStore.selectedModel === key" class="w-3.5 h-3.5 ms-auto text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatStore } from '@/stores/chat'

const { t } = useI18n()
const chatStore = useChatStore()
const open = ref(false)
const dropdownRef = ref(null)
const floatingStyle = ref({})

const modelLabels = computed(() => ({
  llama: t('chat.model_groq'),
  qwen: t('chat.model_hf_qwen'),
  gemma: t('chat.model_hf_gemma'),
}))

const modelColors = {
  llama: 'bg-emerald-500',
  qwen: 'bg-blue-500',
  gemma: 'bg-amber-500',
}

function selectModel(key) {
  chatStore.selectedModel = key
  open.value = false
}

function toggleOpen() {
  if (!open.value) {
    const rect = dropdownRef.value.getBoundingClientRect()
    floatingStyle.value = {
      top: `${rect.bottom + 6}px`,
      left: `${rect.left}px`,
    }
  }
  open.value = !open.value
}

function handleClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    open.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>