from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:  # noqa: D401
        """Generate text/code from a prompt."""


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, AIProvider] = {}

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[AIProvider]:
        return self._providers.get(name)

    def list(self) -> list[str]:
        return list(self._providers.keys())


registry = ProviderRegistry()