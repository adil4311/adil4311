from __future__ import annotations

from typing import Any

import google.generativeai as genai

from backend.core.config import get_settings
from backend.services.providers.base import AIProvider, registry


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self) -> None:
        settings = get_settings()
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
        self.model_name = "gemini-1.5-pro"

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        api_key: str | None = kwargs.get("api_key")
        if api_key:
            genai.configure(api_key=api_key)
        model = genai.GenerativeModel(kwargs.get("model", self.model_name))
        resp = model.generate_content(prompt)
        return resp.text or ""


registry.register(GeminiProvider())