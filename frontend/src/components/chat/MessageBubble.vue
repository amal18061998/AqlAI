<template>
  <!--
    MessageBubble: Single chat message.
    - User messages: right-aligned, indigo background
    - Assistant messages: left-aligned, white background
    - Smooth fade-up entrance animation
    - Supports RTL layout automatically via CSS logical properties
  -->
  <div
    class="flex gap-3 animate-fade-up"
    :class="isUser ? 'justify-end' : 'justify-start'"
  >
    <!-- Avatar (assistant only) -->
    <div v-if="!isUser"
         class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center
                bg-gradient-to-br from-purple-500 to-indigo-600 shadow-sm">
      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
      </svg>
    </div>

    <!-- Bubble -->
    <div
      class="message-bubble max-w-[75%] px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words"
      :class="bubbleClasses"
    >
      {{ message.content }}
    </div>

    <!-- Avatar (user only) -->
    <div v-if="isUser"
         class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center
                bg-stone-200 text-stone-600 text-xs font-bold uppercase">
      {{ userInitial }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  message: { type: Object, required: true },
})

const authStore = useAuthStore()

const isUser = computed(() => props.message.role === 'user')

const userInitial = computed(() =>
  authStore.currentUser?.username?.charAt(0) || 'U'
)

const bubbleClasses = computed(() =>
  isUser.value
    ? 'user bg-indigo-600 text-white rounded-2xl rounded-br-md shadow-sm shadow-indigo-600/15'
    : 'assistant bg-white text-stone-800 rounded-2xl rounded-bl-md shadow-sm border border-stone-100'
)
</script>
