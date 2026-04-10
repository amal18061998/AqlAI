import client from './client'

/**
 * Chat API endpoints.
 * Maps to Django: /api/chat/conversations/, /api/chat/conversations/:id/messages/
 */

export const chatApi = {
  getConversations() {
    return client.get('/chat/conversations/')
  },

  createConversation(data) {
    return client.post('/chat/conversations/', data)
  },

  deleteConversation(id) {
    return client.delete(`/chat/conversations/${id}/`)
  },

  getMessages(conversationId) {
    return client.get(`/chat/conversations/${conversationId}/messages/`)
  },

  sendMessage(conversationId, data) {
    return client.post(`/chat/conversations/${conversationId}/messages/`, data)
  },
  exportPdf(conversationId) {
    return client.get(`/chat/conversations/${conversationId}/export-pdf/`, {
      responseType: 'blob',
    })
  },
}
