from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import auth, projects, ai
from backend.api.routes import settings as settings_routes
from backend.core.config import get_settings
from backend.core.logging import configure_logging


settings = get_settings()
configure_logging(settings.debug)

app = FastAPI(title="HyperAI Builder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.backend_cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(ai.router)
app.include_router(settings_routes.router)


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}