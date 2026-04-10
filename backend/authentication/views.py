"""
Authentication views.

Endpoints:
  POST /api/auth/signup/  -> Create new user, return user data
  POST /api/auth/login/   -> Obtain JWT pair (handled by SimpleJWT, see urls.py)
  POST /api/auth/logout/  -> Blacklist refresh token
  GET  /api/auth/me/      -> Get current user profile
  PATCH /api/auth/me/     -> Update language preference
"""

from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, UserSerializer, UserUpdateSerializer


class SignupView(CreateAPIView):
    """
    POST /api/auth/signup/
    
    Public endpoint. Creates a new user account.
    Returns the created user data (without password).
    """
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    
    Blacklists the provided refresh token so it cannot be reused.
    The access token stays valid until expiry (stateless JWT).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(RetrieveUpdateAPIView):
    """
    GET   /api/auth/me/  -> Return current user profile
    PATCH /api/auth/me/  -> Update language preference
    
    get_object() returns request.user directly (no PK in URL).
    Uses different serializers for read vs write operations.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UserUpdateSerializer
        return UserSerializer
