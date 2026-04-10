<template>
  <!--
    ChatView: Main authenticated chat interface.
    Layout: Sidebar (280px) | Main chat area (flex-1)
    - Header with model selector and mobile sidebar toggle
    - Scrollable message area with auto-scroll to bottom
    - Typing indicator when AI is responding
    - Input bar pinned to bottom
    - Empty state when no conversation selected
  -->
  <div class="h-screen flex  bg-white pt-16">
    
    <!-- Mobile sidebar overlay -->
    <transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0" enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150"
      leave-from-class="opacity-100" leave-to-class="opacity-0"
    >
      <div v-if="sidebarOpen" class="md:hidden fixed inset-0 z-30 bg-black/40"
           @click="sidebarOpen = false"></div>
          
    </transition>

    <!-- Sidebar -->
    <div class="fixed md:relative z-40 h-full w-[280px] transition-transform duration-200"
         :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'">
      <Sidebar :open="true" @close="sidebarOpen = false" />
    </div>

    <!-- Main area -->
    <div class="flex-1 flex flex-col min-w-0">
      <Navbar />
      <!-- Chat header -->
      <header class="shrink-0 h-14 flex items-center justify-between px-4
                     border-b border-stone-200 bg-white/80 backdrop-blur-sm">
                     <ModelSelector />
        <div class="flex items-center gap-3">

          <!-- Mobile sidebar toggle -->
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="md:hidden p-1.5 rounded-lg hover:bg-stone-100 text-stone-500 cursor-pointer"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>

          <h2 class="text-sm font-semibold text-stone-800 truncate max-w-[200px]">
            {{ chatStore.activeConversation?.title || $t('chat.new_chat') }}
          </h2>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- ════════════════════════════════════════════ -->
          <!-- PDF export button (Always visible, disabled if empty) -->
          <!-- ════════════════════════════════════════════ -->
          <button
            @click="handleExportPdf"
            :disabled="exporting || chatStore.messages.length === 0"
            class="p-1.5 rounded-lg text-stone-400 hover:text-indigo-600 hover:bg-indigo-50
                   disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
            :title="$t('chat.export_pdf') || 'Export as PDF'"
          >
            <!-- Download/document icon -->
            <svg v-if="!exporting" class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3M6 20h12a2 2 0 002-2V8l-6-6H6a2 2 0 00-2 2v14a2 2 0 002 2z"/>
            </svg>
            <!-- Spinner while exporting -->
            <svg v-else class="w-4.5 h-4.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
          </button>
          
         <!-- Chat sub-header: title + ModelSelector (always visible) -->
        
        </div>
      </header>

      <!-- Messages area -->
      <div ref="messagesContainer"
           class="flex-1 overflow-y-auto custom-scrollbar px-4 py-6">
        <!-- Empty state -->
        <div v-if="chatStore.messages.length === 0 && !chatStore.typing"
             class="h-full flex flex-col items-center justify-center text-center px-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100
                      flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-stone-800 mb-1">{{ $t('app.name') }}</h3>
          <p class="text-sm text-stone-500 max-w-sm">{{ $t('chat.start_prompt') }}</p>

          <!-- Quick prompts
          <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-md">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              @click="chatStore.sendMessage(prompt)"
              class="px-4 py-3 rounded-xl border border-stone-200 text-sm text-stone-600
                     hover:bg-stone-50 hover:border-stone-300 transition-all text-start cursor-pointer"
            >
              {{ prompt }}
            </button>
          </div> -->
        </div>

        <!-- Messages -->
        <div v-else class="max-w-3xl mx-auto space-y-4">
          <MessageBubble
            v-for="msg in chatStore.messages"
            :key="msg.id"
            :message="msg"
          />

          <!-- Typing indicator -->
          <div v-if="chatStore.typing" class="flex items-center gap-3 animate-fade-up">
            <div class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center
                        bg-gradient-to-br from-purple-500 to-indigo-600 shadow-sm">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div class="bg-white border border-stone-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
              <div class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full bg-stone-400 typing-dot"></div>
                <div class="w-2 h-2 rounded-full bg-stone-400 typing-dot"></div>
                <div class="w-2 h-2 rounded-full bg-stone-400 typing-dot"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error banner -->
      <div v-if="chatStore.error"
           class="shrink-0 px-4 py-2 bg-red-50 border-t border-red-100 flex items-center justify-between">
        <span class="text-sm text-red-600">{{ chatStore.error }}</span>
        <button @click="chatStore.clearError" class="text-red-400 hover:text-red-600 text-sm cursor-pointer">
          {{ $t('common.close') }}
        </button>
      </div>

      <!-- Input -->
      <ChatInput />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import MessageBubble from '@/components/chat/MessageBubble.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ModelSelector from '@/components/chat/ModelSelector.vue'
import LanguageToggle from '@/components/common/LanguageToggle.vue'

const chatStore = useChatStore()
const messagesContainer = ref(null)
const sidebarOpen = ref(false)

// const quickPrompts = [
//   'Explain quantum computing simply',
//   'Write a Python function to sort a list',
//   'What are the benefits of meditation?',
//   'Help me plan a weekend trip',
// ]
const exporting = ref(false)

async function handleExportPdf() {
  if (!chatStore.activeConversationId) return

  exporting.value = true
  try {
    await chatStore.exportPdf()
  } catch (err) {
    console.error('Export failed:', err)
  } finally {
    exporting.value = false // ensures reset even on failure
  }
}
// Auto-scroll when new messages arrive
watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

watch(
  () => chatStore.typing,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

function scrollToBottom() {
  const el = messagesContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

onMounted(() => {
  chatStore.fetchConversations()
})
</script>
