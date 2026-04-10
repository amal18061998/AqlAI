<template>
  <!--
    Sidebar: Left panel in chat view.
    - "New Chat" button at top
    - Scrollable list of past conversations sorted by date
    - Active conversation highlighted
    - Delete button on hover
    - Collapsible on mobile via prop
  -->
  <aside
    class="sidebar flex flex-col h-full bg-stone-50 border-r border-stone-200"
    :class="{ 'translate-x-0': open, '-translate-x-full md:translate-x-0': !open }"
  >
    <!-- New chat button -->
    <div class="p-3 border-b border-stone-200">
      <button
        @click="handleNewChat"
        class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
               bg-indigo-600 text-white text-sm font-semibold
               hover:bg-indigo-700 active:scale-[0.98] transition-all cursor-pointer
               shadow-sm shadow-indigo-600/20"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        {{ $t('chat.new_chat') }}
      </button>
    </div>
    <!-- Search input -->
<div class="p-2 border-b border-stone-200">
  <input
    v-model="searchQuery"
    type="text"
    :placeholder="$t('chat.search')"
    class="w-full px-3 py-2 text-sm rounded-lg border border-stone-200
           focus:outline-none focus:ring-2 focus:ring-indigo-500
           bg-white text-stone-700"
  />
</div>

    <!-- Conversation list -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-0.5">
      <p v-if="chatStore.conversations.length === 0" class="text-center text-stone-400 text-sm mt-8 px-4">
        {{ $t('chat.no_conversations') }}
      </p>
<!-- chatStore.sortedConversations" -->
      <div
        v-for="conv in filteredConversations"
        
        :key="conv.id"
        class="group relative flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer
               transition-colors text-sm"
        :class="conv.id === chatStore.activeConversationId
          ? 'bg-indigo-50 text-indigo-900'
          : 'text-stone-600 hover:bg-stone-100'"
        @click="handleSelect(conv.id)"
      >
        <!-- Chat icon -->
        <svg class="w-4 h-4 shrink-0 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>

        <!-- Title (truncated) -->
        <span class="flex-1 truncate">
          {{ conv.title || $t('chat.new_chat') }}
        </span>

        <!-- Model badge -->
        <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-stone-200/60 text-stone-500
                     shrink-0 hidden group-hover:inline-block">
          {{ conv.model }}
        </span>

        <!-- Delete button -->
        <button
          @click.stop="handleDelete(conv.id)"
          class="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 text-stone-400
                 hover:text-red-500 transition-all cursor-pointer absolute end-1"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useChatStore } from '@/stores/chat'
import { computed, ref } from 'vue'
defineProps({
  open: { type: Boolean, default: true },
})

const emit = defineEmits(['close'])
const chatStore = useChatStore()
const searchQuery = ref('')

const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) {
    return chatStore.sortedConversations
  }

  return chatStore.sortedConversations.filter(conv =>
    (conv.title || '').toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
async function handleNewChat() {
  await chatStore.createConversation()
  emit('close')
}

function handleSelect(id) {
  chatStore.selectConversation(id)
  emit('close')
}

function handleDelete(id) {
  chatStore.deleteConversation(id)
}
</script>
