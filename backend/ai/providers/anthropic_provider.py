from __future__ import annotations

import os

import anthropic


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=key) if key else None

    async def generate(self, prompt: str) -> str:
        if not self.client:
            return "# Missing ANTHROPIC_API_KEY; returning stub code\nprint('Hello')\n"
        try:
            resp = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2048,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )
            # anthropic returns content list
            parts = resp.content
            if parts and hasattr(parts[0], "text"):
                return parts[0].text
            return str(resp)
        except Exception:
            return "# Anthropic error; returning stub\nprint('Hello')\n"