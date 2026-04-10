<template>
  <!--
    ConversationList: Standalone conversation list, reusable.
    Used in Sidebar and could be used in a dedicated history page.
  -->
  <div class="space-y-1">
    <div
      v-for="conv in conversations"
      :key="conv.id"
      class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm"
      :class="conv.id === activeId
        ? 'bg-indigo-50 text-indigo-900 font-medium'
        : 'text-stone-600 hover:bg-stone-100'"
      @click="$emit('select', conv.id)"
    >
      <svg class="w-4 h-4 shrink-0 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
      </svg>
      <span class="flex-1 truncate">{{ conv.title || 'New Chat' }}</span>
      <span class="text-[10px] text-stone-400">{{ formatDate(conv.updated_at) }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conversations: { type: Array, default: () => [] },
  activeId: { type: [Number, String], default: null },
})

defineEmits(['select'])

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 86400000) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  if (diff < 604800000) return d.toLocaleDateString([], { weekday: 'short' })
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}
</script>
