from __future__ import annotations

from typing import Any

from anthropic import AsyncAnthropic

from backend.core.config import get_settings
from backend.services.providers.base import AIProvider, registry


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key or None)

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        api_key: str | None = kwargs.get("api_key")
        client = self.client if not api_key else AsyncAnthropic(api_key=api_key)
        model = kwargs.get("model", "claude-3-5-sonnet-20240620")
        resp = await client.messages.create(
            model=model,
            max_tokens=2048,
            temperature=kwargs.get("temperature", 0.2),
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text if resp.content else ""


registry.register(AnthropicProvider())