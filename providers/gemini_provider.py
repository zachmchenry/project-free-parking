"""
Google Gemini provider.

Requires:
    pip install google-genai
    export GEMINI_API_KEY=...

Uses the new google-genai SDK (the successor to the deprecated
google-generativeai package). Set the model via config.GEMINI_MODEL,
e.g. 'gemini-2.0-flash' or 'gemini-1.5-pro'.

Gemini's native chat shape uses 'user' and 'model' for roles (not
'assistant') and supports a `system_instruction` field on the model
config. We translate the OpenAI-style {role, content} messages we
get into Gemini's shape internally.
"""
import os
from typing import List, Dict

from google import genai
from google.genai import types

from .base import LLMProvider
from config import GEMINI_MODEL


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        self.model = GEMINI_MODEL
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Export it in your shell "
                "before starting the app."
            )
        self.client = genai.Client(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        # Translate openai-style messages -> gemini contents.
        # Gemini uses role='user' and role='model'.
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=m["content"])],
            ))

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return (response.text or "").strip()
