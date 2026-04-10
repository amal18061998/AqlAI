"""
Custom User model.

Extends Django's AbstractUser with two extra fields:
- language: stores the user's preferred language ('en' or 'ar')
- ai_summary: AI-generated text summarizing the user's interests/patterns

Using a custom user model from day one is a Django best practice.
Changing the user model after migrations exist is painful — always
define it upfront even if you only add fields later.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ar", "Arabic"),
    ]

    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en",
        help_text="User's preferred interface and response language.",
    )
    ai_summary = models.TextField(
        blank=True,
        default="",
        help_text="AI-generated summary of user's chat patterns and interests.",
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.username} ({self.language})"
