from __future__ import annotations

import os

from celery import Celery

BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BACKEND_URL = BROKER_URL

celery_app = Celery(
    "hyperai",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=["backend.tasks.codegen"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    task_always_eager=os.getenv("CELERY_EAGER", "0") == "1",
)