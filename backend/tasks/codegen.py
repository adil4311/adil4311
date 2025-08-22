from __future__ import annotations

from celery import shared_task


@shared_task(name="codegen.generate_project")
def generate_project_task(project_id: str, prompt: str, model: str | None) -> str:
    # Placeholder; later call AI providers and write artifacts
    return f"Generated code for {project_id} with model={model}:\n{prompt[:120]}..."