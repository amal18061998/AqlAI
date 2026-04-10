import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi } from '@/api/chat'

/**
 * Chat Store (Pinia)
 * 
 * Manages:
 * - List of conversations (sidebar)
 * - Active conversation and its messages
 * - Selected AI model
 * - Sending messages and receiving AI responses
 * - Loading/typing states for UI feedback
 */

export const useChatStore = defineStore('chat', () => {
  // ── State ──
  const conversations = ref([])
  const activeConversationId = ref(null)
  const messages = ref([])
  const selectedModel = ref('groq')
  const loading = ref(false)
  const typing = ref(false)
  const error = ref(null)

  // ── Getters ──
  const activeConversation = computed(() =>
    conversations.value.find(c => c.id === activeConversationId.value)
  )
  const sortedConversations = computed(() =>
    [...conversations.value].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
  )

  // ── Actions ──
  async function fetchConversations() {
    try {
      const { data } = await chatApi.getConversations()
      conversations.value = data
    } catch (err) {
      error.value = 'Failed to load conversations'
    }
  }

  async function createConversation() {
    try {
      const { data } = await chatApi.createConversation({
        model: selectedModel.value,
      })
      conversations.value.unshift(data)
      activeConversationId.value = data.id
      messages.value = []
      return data
    } catch (err) {
      error.value = 'Failed to create conversation'
    }
  }

  async function selectConversation(id) {
    activeConversationId.value = id
    await fetchMessages(id)
  }

  async function fetchMessages(conversationId) {
    loading.value = true
    try {
      const { data } = await chatApi.getMessages(conversationId)
      messages.value = data
    } catch {
      error.value = 'Failed to load messages'
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(content) {
    if (!content.trim()) return
    
    // Ensure we have an active conversation
    if (!activeConversationId.value) {
      await createConversation()
    }

    // Optimistic UI: add user message immediately
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)
    
    // Show typing indicator
    typing.value = true
    error.value = null

    try {
      const { data } = await chatApi.sendMessage(activeConversationId.value, {
        content: content.trim(),
        model: selectedModel.value,
      })
      // Replace optimistic message + add AI response
      messages.value.pop() // remove optimistic
      messages.value.push(data.user_message)
      messages.value.push(data.ai_message)

      // Update conversation title if it was the first message
      const conv = conversations.value.find(c => c.id === activeConversationId.value)
      if (conv && data.conversation_title) {
        conv.title = data.conversation_title
      }
    } catch (err) {
      error.value = 'Failed to send message'
    } finally {
      typing.value = false
    }
  }

  async function deleteConversation(id) {
    try {
      await chatApi.deleteConversation(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (activeConversationId.value === id) {
        activeConversationId.value = null
        messages.value = []
      }
    } catch {
      error.value = 'Failed to delete conversation'
    }
  }

  function clearError() {
    error.value = null
  }
  async function exportPdf() {
    if (!activeConversationId.value) return
  
    const response = await chatApi.exportPdf(this.activeConversationId)
  
    const url = window.URL.createObjectURL(response.data)
  
    const a = document.createElement('a')
    a.href = url
    a.download = 'conversation.pdf'
    a.click()
  
    window.URL.revokeObjectURL(url)
  }
  
  return {
    conversations, activeConversationId, messages,
    selectedModel, loading, typing, error,
    activeConversation, sortedConversations,
    fetchConversations, createConversation, selectConversation,
    sendMessage, deleteConversation, clearError,exportPdf,
  }
})
