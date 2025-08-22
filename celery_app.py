from __future__ import annotations

import os
from celery import Celery


def make_celery() -> Celery:
    broker = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
    backend = os.getenv("REDIS_RESULT_BACKEND", "redis://localhost:6379/1")
    celery = Celery("hyperai", broker=broker, backend=backend)
    celery.autodiscover_tasks(["backend.services.tasks"])
    return celery


celery_app = make_celery()