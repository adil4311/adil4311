from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import settings
from .db import init_db
from .routers import auth as auth_router
from .routers import projects as projects_router
from .ai import ai_manager
from .ai.providers import OpenAIProvider
from .ai.providers import AnthropicProvider
from .ai.providers import GeminiProvider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting HyperAI Builder backend")
    await init_db()
    # Register AI providers
    ai_manager.register(OpenAIProvider(settings.openai_api_key))
    ai_manager.register(AnthropicProvider(settings.anthropic_api_key))
    ai_manager.register(GeminiProvider(settings.google_api_key))
    yield
    logger.info("Shutting down HyperAI Builder backend")


app = FastAPI(
    title="HyperAI Builder API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router.router, prefix="/api/projects", tags=["projects"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}