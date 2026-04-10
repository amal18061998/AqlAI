from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Extend default UserAdmin to show our custom fields."""
    list_display = ("username", "email", "language", "date_joined")
    list_filter = ("language", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("AI_CHATBOT", {"fields": ("language", "ai_summary")}),
    )
