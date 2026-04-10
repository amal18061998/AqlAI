"""
Authentication serializers.

Three serializers handle all auth data flow:
- SignupSerializer: validates new user registration data, hashes password
- UserSerializer: reads user profile (used by GET /api/auth/me/)
- UserUpdateSerializer: partial updates (language preference)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    """
    Handles user registration.
    
    - password is write-only (never returned in responses)
    - create() uses set_password() to hash the password properly
    - email is required (Django's default makes it optional)
    """

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "language")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            language=validated_data.get("language", "en"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only user profile serializer.
    Includes ai_summary and date_joined for the profile page.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "language",
            "ai_summary",
            "date_joined",
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Partial update serializer.
    Currently only language can be updated from the frontend.
    """

    class Meta:
        model = User
        fields = ("language",)
