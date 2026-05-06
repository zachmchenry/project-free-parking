"""
LLM provider abstraction.

The application code calls LLMProvider.chat(messages, system) and gets
back a string. Which provider answers is configured in config.py.

To add a new provider, subclass LLMProvider in a new file and register
it in get_provider() at the bottom of this module.
"""
from .base import LLMProvider


def get_provider(name: str) -> LLMProvider:
    """
    Factory: return a configured LLMProvider for the named backend.
    Imports are deferred so a missing SDK doesn't crash the whole app —
    only the provider you're actually using needs to be installed.
    """
    name = name.lower().strip()
    if name == "claude" or name == "anthropic":
        from .claude_provider import ClaudeProvider
        return ClaudeProvider()
    if name == "openai" or name == "chatgpt":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    if name == "bedrock" or name == "aws":
        from .bedrock_provider import BedrockProvider
        return BedrockProvider()
    if name == "gemini" or name == "google":
        from .gemini_provider import GeminiProvider
        return GeminiProvider()
    raise ValueError(
        f"Unknown provider: {name!r}. "
        f"Valid: claude, openai, bedrock, gemini."
    )
