from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from backend.core.config import get_settings
from backend.services.providers.base import AIProvider, registry


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key or None)

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        api_key: str | None = kwargs.get("api_key")
        client = self.client if not api_key else AsyncOpenAI(api_key=api_key)
        model = kwargs.get("model", "gpt-4o-mini")
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.2),
        )
        return resp.choices[0].message.content or ""


registry.register(OpenAIProvider())