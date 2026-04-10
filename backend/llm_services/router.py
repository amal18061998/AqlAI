"""
AI Provider Router.

Maps model selection strings to provider classes.
Now uses 3 models:
  - 'groq'        -> Groq API (LLaMA 3.3 70B) — fast, capable
  - 'qwen'     -> HuggingFace Qwen 2.5 7B — good multilingual
  - 'gemma'    -> HuggingFace Gemma 2 2B — fast, lightweight
"""

from .huggingfaceBase_provider import HuggingFaceGemmaProvider, HuggingFaceQwenProvider
from .groqBase_provider import GroqLlamaProvider

PROVIDERS = {
    "gemma": HuggingFaceGemmaProvider(),
    "qwen": HuggingFaceQwenProvider(),
    "llama": GroqLlamaProvider(),
    
}


def get_ai_response(
    messages: list[dict],
    model: str = "llama",
    language: str = "en",
) -> str:
    """
    Route a chat request to the appropriate AI provider.

    Args:
        messages: Conversation history
        model: Provider key ('llama', 'qwen', 'gemma')
        language: User's language ('en' or 'ar')

    Returns:
        AI response text.
    """
    provider = PROVIDERS.get(model)
    if not provider:
        provider = PROVIDERS["llama"]

    return provider.generate_response(messages, language)
