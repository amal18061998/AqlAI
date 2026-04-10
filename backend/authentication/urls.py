"""
Authentication URL patterns.

  POST /api/auth/signup/          -> SignupView
  POST /api/auth/login/           -> SimpleJWT TokenObtainPairView
  POST /api/auth/login/refresh/   -> SimpleJWT TokenRefreshView
  POST /api/auth/logout/          -> LogoutView
  GET/PATCH /api/auth/me/         -> ProfileView

Note: login/ uses SimpleJWT's built-in view directly.
It accepts { "username": "...", "password": "..." }
and returns { "access": "...", "refresh": "..." }.
No custom view needed.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView, LogoutView, ProfileView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ProfileView.as_view(), name="profile"),
]
