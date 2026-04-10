"""
Abstract base class for AI providers.

Every AI provider (Groq, HuggingFace) inherits from this
and implements generate_response(). This makes adding new providers
trivial — just create a new file, subclass AIProvider, and register
it in router.py.

"""

from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Base class for all AI model providers."""

    @abstractmethod
    def generate_response(
        self,
        messages: list[dict],
        language: str = "en",
    ) -> str:
        """
        Generate a response from the AI model.

        Args:
            messages: Conversation history as a list of role/content dicts.
            language: User's preferred language ('en' or 'ar').

        Returns:
            The AI model's response as a string.

        Raises:
            Exception: If the API call fails.
        """
        pass

    def _build_system_prompt(self, language: str) -> str:
        """
        Build a system prompt that instructs the AI to respond
        in the user's preferred language.First, detect the language the user is writing in. 
        Then, always respond in that exact same language, mirroring the user's input without exception.
        Never switch languages unless the user switches first.
        If the message contains multiple languages, respond in the dominant one.
        """
        if language == "ar":
            return (
                "You are a helpful AI assistant. "
                "You MUST ALWAYS respond ONLY in Arabic. "
                "Always respond in Arabic (العربية). "
                "Use formal Modern Standard Arabic. "
                "Be clear, concise, and culturally appropriate."
            )
        return (
            "You MUST ALWAYS respond ONLY in English. "
            "Do NOT use any other language, even if previous messages were in another language."
            "You are a helpful AI assistant. "
            "Respond in English. Be clear, concise, and helpful."
        )
