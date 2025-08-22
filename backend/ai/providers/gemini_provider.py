from __future__ import annotations

import os

import google.generativeai as genai


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def generate(self, prompt: str) -> str:
        if not self.model:
            return "# Missing GOOGLE_API_KEY; returning stub code\nprint('Hello')\n"
        try:
            resp = self.model.generate_content(prompt)
            return resp.text or ""
        except Exception:
            return "# Gemini error; returning stub\nprint('Hello')\n"