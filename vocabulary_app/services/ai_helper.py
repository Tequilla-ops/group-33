"""AI Helper service abstraction for generating explanations and memory tricks."""

import os
import re
import json
from typing import Optional
import requests

class AIHelper:
    """Abstraction layer for AI generation using OpenAI API (supports environment variables)."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("AI_API_KEY")

    def is_available(self) -> bool:
        """Check if AI API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def generate_enhancements(self, word: str, definition: str) -> dict:
        """Generate simple explanation, example sentence, and memory trick.

        If AI is unavailable or fails, returns intelligent local fallbacks
        so the application remains fully functional.
        """
        if not self.is_available():
            return self._get_fallback(word, definition)

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            prompt = (
                f"You are a friendly vocabulary learning assistant. Help the student learn the word '{word}' which has the definition: '{definition}'. "
                "Respond with a JSON object containing exactly three keys:\n"
                "1. 'ai_explanation': A simple, engaging explanation of the word's meaning.\n"
                "2. 'ai_example': A simple, clear example sentence demonstrating how the word is used.\n"
                "3. 'memory_trick': A clever memory trick or mnemonic to help the student remember the word.\n"
                "Only return valid JSON without markdown wrapping."
            )
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            explanation = parsed.get("ai_explanation")
            trick = parsed.get("memory_trick")
            example = parsed.get("ai_example")

            if not explanation or not trick:
                return self._get_fallback(word, definition)

            return {
                "ai_explanation": str(explanation).strip(),
                "memory_trick": str(trick).strip(),
                "ai_example": str(example).strip() if example else None,
            }
        except Exception:
            # Fallback gracefully if API call fails (e.g. invalid key, offline, timeout)
            return self._get_fallback(word, definition)

    def _get_fallback(self, word: str, definition: str) -> dict:
        """Generate educational offline fallback explanations and mnemonics using regex/string cleaning."""
        clean_word = re.sub(r"[^a-zA-Z]", "", word).capitalize()
        explanation = f"In simple terms, '{clean_word}' means: {definition}"
        trick = f"Memory Tip: Associate '{clean_word}' with its definition by picturing it in a vivid sentence."
        example = f"Example: The situation felt completely {clean_word.lower()} in nature."
        return {
            "ai_explanation": explanation,
            "memory_trick": trick,
            "ai_example": example,
        }
