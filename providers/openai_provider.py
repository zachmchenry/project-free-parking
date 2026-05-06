"""
OpenAI provider (GPT models accessed via the OpenAI Python SDK).

Requires:
    pip install openai
    export OPENAI_API_KEY=...

The model is set via config.OPENAI_MODEL. Recommended values include
'gpt-4o', 'gpt-4o-mini', or whichever current model is preferred. For
this exercise gpt-4o handles the persona well.
"""
import os
from typing import List, Dict

from openai import OpenAI

from .base import LLMProvider
from config import OPENAI_MODEL


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self):
        self.model = OPENAI_MODEL
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. Export it in your shell "
                "before starting the app."
            )
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        # OpenAI: system message goes inline at the start of the messages list.
        full_messages = [{"role": "system", "content": system}] + messages
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
