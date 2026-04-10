"""
Root URL configuration.

All API endpoints live under /api/ prefix:
  /api/auth/   → authentication app (signup, login, logout, profile)
  /api/chat/   → chat app (conversations, messages)
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/chat/", include("chat.urls")),
]