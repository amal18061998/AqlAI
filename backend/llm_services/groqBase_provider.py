import requests
from django.conf import settings
from .IProvider import AIProvider

class GroqBaseProvider(AIProvider):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, messages, language="en"):
        api_key = settings.GROQ_API_KEY

        if not api_key:
            return self._fallback_response(language)

        system_msg = {
            "role": "system",
            "content": self._build_system_prompt(language),
        }

        full_messages = [system_msg] + messages

        try:
            response = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.MODEL,
                    "messages": full_messages,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            return self._fallback_response(language, str(e))

class GroqLlamaProvider(GroqBaseProvider):
    MODEL = "llama-3.3-70b-versatile"
      