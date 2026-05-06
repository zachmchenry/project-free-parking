"""
Abstract base for LLM providers.

Every provider implements `chat(messages, system) -> str`. The shape of
`messages` is the OpenAI-style list of {role, content} dicts. Providers
adapt this to their native shape internally.

The base class also defines a standard role mapping. Some providers
(Gemini, older Bedrock APIs) use different role names; converters live
in the provider implementations, not here.
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class LLMProvider(ABC):
    """
    Subclass this and implement `chat()`.
    """

    # Subclasses set these for diagnostics
    name: str = "abstract"
    model: str = "abstract"

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat completion request and return the assistant text.

        Parameters
        ----------
        messages : list of dict
            Conversation history. Each dict has keys 'role' (one of
            'user' or 'assistant') and 'content' (string). Does NOT
            include the system message — that is passed separately.
        system : str
            System prompt. Most providers send this as a separate
            field; some (older Gemini) do not support it natively
            and prepend it to the first user message.
        max_tokens : int
        temperature : float

        Returns
        -------
        str : the assistant's reply text.
        """
        raise NotImplementedError

    def describe(self) -> str:
        """Used in the /health endpoint to report which provider is wired up."""
        return f"{self.name} ({self.model})"
