# HyperAI Builder

HyperAI Builder is a professional-grade, no-code AI application builder.
It combines a Streamlit frontend and a FastAPI backend to generate
production-ready applications using leading AI models (OpenAI, Anthropic,
Google Gemini), with async processing, security, and tests.

## Quickstart

1. Python 3.11+
2. Create and populate `.env` from `.env.example`
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run backend:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

5. Run frontend:

```bash
streamlit run frontend/app.py
```

## Features
- Streamlit multi-step project wizard
- FastAPI with JWT auth
- Async SQLAlchemy (SQLite dev, PostgreSQL prod)
- Celery + Redis for background tasks
- AI providers: OpenAI, Anthropic, Google Gemini (pluggable)
- Secure key storage with encryption
- Code generation with tests and deployment artifacts

## License
MIT