"""
Chat models.

Two models handle all chat data:

Conversation:
  - Belongs to a user (FK)
  - Stores the AI model used for this conversation
  - Title is auto-generated from the first message
  - Timestamps for sorting (updated_at changes on every new message)

Message:
  - Belongs to a conversation (FK)
  - role: 'user' or 'assistant'
  - content: the actual message text
  - Ordered by creation time
"""

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    MODEL_CHOICES = [
        ("llama", "Groq (LLaMA 3.3)"),
        ("qwen", "HuggingFace (Qwen 2.5)"),
        ("gemma", "HuggingFace (Gemma 2)"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    model = models.CharField(max_length=50, choices=MODEL_CHOICES, default="groq")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"[{self.model}] {self.title or 'Untitled'} — {self.user.username}"



class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"[{self.role}] {preview}"
