from __future__ import annotations

from typing import Protocol


class Provider(Protocol):
    name: str

    async def generate(self, prompt: str) -> str: ...


class AIManager:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider

    async def generate(self, prompt: str, model: str | None = None) -> str:
        if model and model in self._providers:
            return await self._providers[model].generate(prompt)
        # fallback to first provider
        if self._providers:
            provider = next(iter(self._providers.values()))
            return await provider.generate(prompt)
        raise RuntimeError("No AI providers registered")


ai_manager = AIManager()