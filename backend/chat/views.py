"""
Chat views.

Endpoints:
  GET    /api/chat/conversations/              -> List user's conversations
  POST   /api/chat/conversations/              -> Create a new conversation
  DELETE /api/chat/conversations/:id/          -> Delete a conversation
  GET    /api/chat/conversations/:id/messages/ -> Get messages for a conversation
  POST   /api/chat/conversations/:id/messages/ -> Send message + get AI response

The MessagesView.post() is the most complex — handles the full message lifecycle:
  1. Validates the user's message
  2. Saves it to the database
  3. Builds conversation history for context
  4. Calls the AI provider via the router
  5. Saves the AI response
  6. Auto-generates conversation title from first message
  7. Triggers user summary update every 10 messages
  8. Returns both messages to the frontend
"""

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)
from llm_services import get_ai_response, generate_user_summary


class ConversationListCreateView(ListCreateAPIView):
    """
    GET  /api/chat/conversations/  -> List all conversations for current user
    POST /api/chat/conversations/  -> Create a new empty conversation

    annotate(message_count=...) adds the count inline so the frontend
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(user=self.request.user)
            .annotate(message_count=Count("messages"))
            .order_by("-updated_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDeleteView(DestroyAPIView):
    """
    DELETE /api/chat/conversations/:id/
    Only allows deleting your own conversations.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class MessagesView(APIView):
    """
    GET  /api/chat/conversations/:id/messages/ -> List all messages
    POST /api/chat/conversations/:id/messages/ -> Send message + get AI reply

    POST request body:
      { "content": "How does AI work?", "model": "groq" }

    POST response 201:
      {
        "user_message": { ... },
        "ai_message": { ... },
        "conversation_title": "How does AI work"
      }
    """
    permission_classes = [IsAuthenticated]

    def _get_conversation(self, request, conversation_id):
        """Helper: fetch conversation or return None."""
        try:
            return Conversation.objects.get(
                id=conversation_id, user=request.user
            )
        except Conversation.DoesNotExist:
            return None

    def get(self, request, conversation_id):
        """Return all messages in a conversation."""
        conversation = self._get_conversation(request, conversation_id)
        if not conversation:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        """Send a message and get AI response."""
        # 1. Validate input
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"]
        model_override = serializer.validated_data.get("model")

        # 2. Get conversation
        conversation = self._get_conversation(request, conversation_id)
        if not conversation:
            return Response(
                {"detail": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update model if overridden
        model = model_override or conversation.model
        if model_override and model_override != conversation.model:
            conversation.model = model_override
            conversation.save(update_fields=["model"])

        # 3. Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=content,
        )

        # 4. Build conversation history (last 20 messages for context)
        history = list(
            conversation.messages
            .order_by("-created_at")[:20]
            .values("role", "content")
        )
        history.reverse()  # Oldest first for the AI

        # 5. Call AI provider
        language = request.user.language
        ai_response_text = get_ai_response(
            messages=history,
            model=model,
            language=language,
        )

        # 6. Save AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_response_text,
        )

        # 7. Auto-generate title
        if not conversation.title:
            conversation.title = content[:60].strip()
            conversation.save(update_fields=["title"])

        # Touch updated_at
        conversation.save(update_fields=["updated_at"])

        # 8. Trigger summary update (Decoupled Logic)
        self._update_user_summary_async(request.user)

        # 9. Return response
        return Response(
            {
                "user_message": MessageSerializer(user_message).data,
                "ai_message": MessageSerializer(ai_message).data,
                "conversation_title": conversation.title,
            },
            status=status.HTTP_201_CREATED,
        )
    def _update_user_summary_async(self, user):
        """
        Helper to trigger summary update every 10 messages.
        Keeps the main post method clean.
        """
        total_user_msgs = Message.objects.filter(
            conversation__user=user, role="user"
        ).count()

        if total_user_msgs % 10 == 0:
            try:
                summary = generate_user_summary(user)
                if summary:
                    user.ai_summary = summary
                    user.save(update_fields=["ai_summary"])
            except Exception:
                pass 
