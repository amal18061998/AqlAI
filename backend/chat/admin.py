from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "model", "message_count", "updated_at")
    list_filter = ("model", "created_at")
    search_fields = ("title", "user__username")
    inlines = [MessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("short_content", "role", "conversation", "created_at")
    list_filter = ("role", "created_at")

    def short_content(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    short_content.short_description = "Content"
