<template>
  <!--
    ChatInput: Bottom bar of the chat view.
    - Auto-growing textarea (up to 5 rows)
    - Send button (disabled while typing/empty)
    - Enter to send, Shift+Enter for new line
  -->
  <div class="chat-input-area border-t border-stone-200 bg-white p-3 sm:p-4">
    <div class="max-w-3xl mx-auto flex items-end gap-2">
      <!-- Textarea wrapper -->
      <div class="flex-1 relative">
        <textarea
          ref="inputRef"
          v-model="text"
          :placeholder="$t('chat.placeholder')"
          rows="1"
          class="w-full resize-none rounded-xl border border-stone-200 bg-stone-50
                 px-4 py-3 text-sm text-stone-800 placeholder-stone-400
                 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400
                 transition-all custom-scrollbar"
          style="max-height: 140px"
          @keydown.enter.exact.prevent="handleSend"
          @input="autoResize"
        ></textarea>
      </div>

      <!-- Send button -->
      <button
        @click="handleSend"
        :disabled="!text.trim() || chatStore.typing"
        class="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center
               transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed
               shadow-sm"
        :class="text.trim() && !chatStore.typing
          ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-600/20'
          : 'bg-stone-100 text-stone-400'"
      >
        <svg class="w-4 h-4" :class="{ 'rotate-90 rtl:-rotate-90': true }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 19V5m0 0l-7 7m7-7l7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const text = ref('')
const inputRef = ref(null)

function handleSend() {
  if (!text.value.trim() || chatStore.typing) return
  chatStore.sendMessage(text.value)
  text.value = ''
  // Reset textarea height
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
}

function autoResize() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

onMounted(() => {
  inputRef.value?.focus()
})
</script>
