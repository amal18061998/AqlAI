#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  Database & Model Test — Tests Django ORM layer directly
  
  Run: python manage.py shell < test_models.py
  
  OR: python manage.py shell
       >>> exec(open('test_models.py').read())
  
  Tests models, relationships, and queries without HTTP.
═══════════════════════════════════════════════════════════════
"""

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Conversation, Message

User = get_user_model()

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  {GREEN}✓ {name}{RESET}")
    else:
        failed += 1
        print(f"  {RED}✗ {name}{RESET}")
    if detail:
        print(f"    {detail}")


print(f"\n{BOLD}{CYAN}═══ Model & Database Tests ═══{RESET}\n")

# ── 1. Create user ──
print(f"{BOLD}1. CustomUser model{RESET}")
user = User.objects.create_user(
    username="model_test_user",
    email="model_test@example.com",
    password="TestPass123",
    language="en",
)
check("User created", user.pk is not None, f"id={user.pk}")
check("Default language is 'en'", user.language == "en")
check("ai_summary default is empty", user.ai_summary == "")
check("String representation", "model_test_user" in str(user))

# Update language
user.language = "ar"
user.save()
user.refresh_from_db()
check("Language updated to 'ar'", user.language == "ar")

# Update summary
user.ai_summary = "User is interested in AI and Python programming."
user.save()
user.refresh_from_db()
check("AI summary saved", "AI" in user.ai_summary)

# ── 2. Conversation model ──
print(f"\n{BOLD}2. Conversation model{RESET}")
conv = Conversation.objects.create(
    user=user,
    title="Test conversation",
    model="groq",
)
check("Conversation created", conv.pk is not None, f"id={conv.pk}")
check("Model is 'groq'", conv.model == "groq")
check("Belongs to user", conv.user == user)
check("String representation", "Test conversation" in str(conv))

# ── 3. Message model ──
print(f"\n{BOLD}3. Message model{RESET}")
msg_user = Message.objects.create(
    conversation=conv,
    role="user",
    content="Hello, how are you?",
)
msg_ai = Message.objects.create(
    conversation=conv,
    role="assistant",
    content="I'm doing well! How can I help you?",
)
check("User message created", msg_user.pk is not None)
check("AI message created", msg_ai.pk is not None)
check("User message role", msg_user.role == "user")
check("AI message role", msg_ai.role == "assistant")

# ── 4. Relationships ──
print(f"\n{BOLD}4. Relationships & queries{RESET}")
check(
    "Conversation has 2 messages",
    conv.messages.count() == 2,
    f"Count: {conv.messages.count()}",
)
check(
    "message_count property",
    conv.message_count == 2,
)
check(
    "User has 1 conversation",
    user.conversations.count() == 1,
)
check(
    "Messages ordered by created_at",
    list(conv.messages.values_list("role", flat=True)) == ["user", "assistant"],
)

# ── 5. Cascade delete ──
print(f"\n{BOLD}5. Cascade delete{RESET}")
conv_id = conv.pk
msg_count_before = Message.objects.filter(conversation_id=conv_id).count()
conv.delete()
msg_count_after = Message.objects.filter(conversation_id=conv_id).count()
check(
    "Deleting conversation removes messages",
    msg_count_before == 2 and msg_count_after == 0,
    f"Before: {msg_count_before}, After: {msg_count_after}",
)

# ── 6. Multiple conversations ──
print(f"\n{BOLD}6. Multiple conversations with different models{RESET}")
conv1 = Conversation.objects.create(user=user, model="groq", title="Groq chat")
conv2 = Conversation.objects.create(user=user, model="huggingface", title="HF chat")

check("2 conversations created", user.conversations.count() == 3)
check(
    "Filter by model works",
    Conversation.objects.filter(user=user, model="deepseek").count() == 1,
)
check(
    "Ordered by -updated_at (default)",
    list(user.conversations.values_list("title", flat=True))[0] == "HF chat",
    "Most recent first",
)

# ── Cleanup ──
print(f"\n{BOLD}Cleanup{RESET}")
user.delete()
check("Test user deleted", not User.objects.filter(username="model_test_user").exists())
check(
    "Conversations cascade-deleted",
    not Conversation.objects.filter(title__in=["Groq chat", "HF chat"]).exists(),
)

# ── Summary ──
total = passed + failed
print(f"\n{'═' * 50}")
print(f"{BOLD}RESULTS: {passed}/{total} passed{RESET}")
if failed == 0:
    print(f"{GREEN}{BOLD}All model tests passed!{RESET}")
else:
    print(f"{RED}{BOLD}{failed} test(s) failed{RESET}")
print(f"{'═' * 50}\n")
