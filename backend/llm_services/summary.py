# llm_services/summary.py
from django.conf import settings
from chat.models import Message
from .router import get_ai_response  # Import the central router function

def generate_user_summary(user) -> str:
    """
    Generates a summary of the user's behavior based on recent message history.
    Uses the central router to select the AI provider.
    """
    # 1. Fetch recent messages only (Safety: limit to last 50 to avoid token overflow)
    messages = Message.objects.filter(
        conversation__user=user,
        role="user",
    ).order_by("-created_at")[:50].values_list("content", flat=True)

    messages_list = list(messages)
    
    if not messages_list:
        return ""

    # 2. Build the Prompt
    lang = user.language
    
    if lang == "ar":
        prompt_text = (
            "أنت محلل سلوك مستخدم. بناءً على الرسائل التالية، اكتب ملخصًا قصيرًا (2-3 جمل).\n"
            "ركز على: اهتمامات المستخدم، المواضيع المتكررة، وأسلوب التواصل.\n\n"
            "الرسائل:\n"
        )
    else:
        prompt_text = (
            "You are a user behavior analyst. Based on the following messages, write a concise summary (2-3 sentences).\n"
            "Focus on: User interests, recurring topics, and communication style.\n\n"
            "Messages:\n"
        )

    # Add messages to prompt (reverse to get chronological order)
    formatted_msgs = "\n".join(f"- {msg}" for msg in reversed(messages_list))
    full_prompt = prompt_text + formatted_msgs

    # 3. Select Model for Summarization
    # Strategy: Use 'groq' if available (better reasoning), else fallback to 'hf_qwen'
    # You can change this logic easily since we use the router.
    preferred_model = "llama"
    
    # Optional: Check if Groq is configured, if not, use Qwen
    # Since your router defaults to groq, we can just call it. 
    # But if you want to force a cheaper model for summaries, change 'preferred_model' to 'hf_qwen'.

    # 4. Call AI via Router
    try:
        summary = get_ai_response(
            messages=[{"role": "user", "content": full_prompt}],
            model=preferred_model,
            language=lang,
        )
        return summary.strip()
        
    except Exception as e:
        print(f"Summary generation failed: {e}")
        return ""