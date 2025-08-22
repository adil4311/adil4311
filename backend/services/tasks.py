from __future__ import annotations

from typing import Any

from celery import shared_task

from backend.services.orchestrator import OrchestratorService


@shared_task(name="generate_code_scaffold")
def generate_code_scaffold_task(description: str, provider: str = "openai") -> dict[str, Any]:
    import asyncio

    service = OrchestratorService()
    result = asyncio.run(service.generate_code_scaffold(description, provider=provider))
    # Here we would persist results, push to repo, etc.
    return {"status": "completed", "length": len(result)}