"""
Chat URL patterns.

  GET/POST   /api/chat/conversations/                -> List/Create conversations
  DELETE     /api/chat/conversations/:id/             -> Delete conversation
  GET/POST   /api/chat/conversations/:id/messages/    -> List messages / Send message

Note: MessageListView and SendMessageView are combined into a single
MessagesView that handles both GET (list) and POST (send).
"""

from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDeleteView,
    MessagesView,
)
from .export_pdf import ExportPdfView  
urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "conversations/<int:pk>/",
        ConversationDeleteView.as_view(),
        name="conversation-delete",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        MessagesView.as_view(),
        name="messages",
    ),
    path(
        "conversations/<int:conversation_id>/export-pdf/",
        ExportPdfView.as_view(),
        name="export-pdf",
    ),
]
