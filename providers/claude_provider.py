"""
Anthropic Claude provider.

Requires:
    pip install anthropic
    export ANTHROPIC_API_KEY=...

The model name is set via config.CLAUDE_MODEL. As of this writing, recommended
values are 'claude-opus-4-7', 'claude-opus-4-6', 'claude-sonnet-4-6', or
'claude-haiku-4-5-20251001'. Sonnet is the cost/quality default for this
exercise.
"""
import os
from typing import List, Dict

from anthropic import Anthropic

from .base import LLMProvider
from config import CLAUDE_MODEL


class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self):
        self.model = CLAUDE_MODEL
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Export it in your shell "
                "before starting the app."
            )
        self.client = Anthropic(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        # Claude takes `system` as a top-level field and `messages` as
        # alternating user/assistant turns — exactly the shape we use.
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
        )
        # response.content is a list of content blocks; we return text only
        parts = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts).strip()
