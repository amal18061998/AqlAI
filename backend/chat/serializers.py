"""
Chat serializers.

ConversationSerializer:
  - Lists conversations for the sidebar
  - Includes message_count as a computed field
  - read-only for most fields (created/updated automatically)

MessageSerializer:
  - Serializes individual messages
  - role and content are the main fields

SendMessageSerializer:
  - Validates incoming user messages
  - content: the user's query text
  - model: which AI provider to use (optional override)
"""

from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "role", "content", "created_at")
        read_only_fields = ("id", "role", "created_at")


class ConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "title",
            "model",
            "message_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "title", "created_at", "updated_at")


class SendMessageSerializer(serializers.Serializer):
    """
    Input serializer for POST /api/chat/conversations/:id/messages/
    
    The frontend sends:
      { "content": "How does AI work?", "model": "groq" }
    """
    content = serializers.CharField(max_length=4000)
    model = serializers.ChoiceField(
        choices=["llama", "qwen", "gemma"],
        required=False,
    )
