# HyperAI Builder

Ultra-advanced AI App Builder: Streamlit frontend + FastAPI backend, with
OpenAI/Anthropic/Gemini integrations, Celery for async tasks, and SQLAlchemy.

## Quickstart

1) Python 3.11+

2) Create and fill `.env` from `.env.example` (generate `FERNET_SECRET_KEY`).

3) Install deps:
```
pip install -r requirements.txt
```

4) Run database migrations:
```
alembic upgrade head
```

5) Run backend API:
```
uvicorn backend.main:app --reload
```

6) Run Streamlit UI:
```
streamlit run frontend/app.py
```

7) (Optional) Run Celery worker:
```
celery -A celery_app.celery_app worker -l info
```

## Environment

- `DATABASE_URL` supports SQLite for dev and Postgres in prod
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` for providers
- `REDIS_BROKER_URL`, `REDIS_RESULT_BACKEND` for Celery

## Project Structure

- `backend/` FastAPI app, models, schemas, services
- `frontend/` Streamlit web UI
- `alembic/` Migrations
- `tests/` Unit/integration tests
- `deploy/` Docker, CI/CD, scripts

## Security

- JWT auth, hashed passwords, CORS
- Input validation with Pydantic
- Encryption helper for API keys (coming in next iteration)

## Roadmap

- Full code generation to repo with GitHub Actions
- RAG templates and plugins
- Advanced UI with components and animations