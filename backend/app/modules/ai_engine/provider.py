from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class AIProviderRequest:
    """Provider-neutral request passed to any model implementation."""

    conversation_id: int
    prompt: str
    conversation_text: str = ""
    messages: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    response_schema: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AIProviderResponse:
    """Provider-neutral response with optional structured output."""

    content: str
    structured_output: Mapping[str, Any]
    model_name: str | None = None
    usage: Mapping[str, int] = field(default_factory=dict)


class AIProviderError(RuntimeError):
    """Raised when a provider fails or returns an invalid response."""


class AIProvider(ABC):
    """Unified interface for DeepSeek, Qwen, Zhipu and local model adapters."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return a stable provider identifier."""

    @abstractmethod
    async def analyze(self, request: AIProviderRequest) -> AIProviderResponse:
        """Analyze a conversation and return provider-neutral structured data."""
