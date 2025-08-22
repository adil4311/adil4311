from __future__ import annotations

import os

from openai import AsyncOpenAI


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def generate(self, prompt: str) -> str:
        if not self.client.api_key:
            return "# Missing OPENAI_API_KEY; returning stub code\nprint('Hello')\n"
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""
        except Exception:
            return "# OpenAI error; returning stub\nprint('Hello')\n"