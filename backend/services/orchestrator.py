from __future__ import annotations

from textwrap import dedent
from typing import Any

from backend.services.providers.base import registry


BLUEPRINT_PROMPT = dedent(
    """
    You are a principal engineer. Given the product description, propose a
    highly professional architecture blueprint. Include:
    - Suggested stack (frontend, backend, DB, infra)
    - Microservices and responsibilities
    - Data model sketch
    - Sequence diagram steps
    - Security & compliance notes
    - Testing and CI/CD strategy
    - Performance and caching plan

    Output markdown. Include Mermaid diagrams for ERD and sequence where useful.

    Description: {description}
    """
)


CODE_SCAFFOLD_PROMPT = dedent(
    """
    You are generating production-ready code. Provide a minimal, runnable
    scaffold for the described app, adhering to PEP-8, type hints, and
    clean architecture. Include:
    - backend service (FastAPI/Flask)
    - optional frontend (Next.js/React) with accessibility
    - database models and migrations
    - docker-compose with DB and cache
    - README instructions
    - basic tests (pytest)

    Return code blocks grouped by filenames. Keep each block concise but runnable.

    App Description: {description}
    """
)


class OrchestratorService:
    async def generate_blueprint(
        self, description: str, provider: str = "openai", api_key: str | None = None
    ) -> str:
        model = registry.get(provider)
        if not model:
            raise ValueError(f"Unknown provider: {provider}")
        prompt = BLUEPRINT_PROMPT.format(description=description)
        return await model.generate(prompt, api_key=api_key)

    async def generate_code_scaffold(
        self, description: str, provider: str = "openai", api_key: str | None = None
    ) -> str:
        model = registry.get(provider)
        if not model:
            raise ValueError(f"Unknown provider: {provider}")
        prompt = CODE_SCAFFOLD_PROMPT.format(description=description)
        return await model.generate(prompt, api_key=api_key)