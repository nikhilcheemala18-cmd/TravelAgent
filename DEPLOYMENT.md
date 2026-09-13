# Deployment and Configuration Notes

Technical setup notes for running the existing FastAPI + React application.
This file documents environment configuration only; it does not change the
application architecture or capability claims.

## Frontend

Required Vite environment variable:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Use the backend origin only. The frontend API client appends `/api/v1` before
calling `/chat` or `/health`.

Production example shape:

```bash
VITE_API_BASE_URL=https://your-backend.example.com
```

Do not include `/api/v1` in new frontend environment values.

## Backend

Common backend environment variables:

```bash
LLM_PROVIDER=mock
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=
LLM_BASE_URL=
FALLBACK_MAX_RETRIES=2
FALLBACK_RETRY_DELAY_MS=250
```

Provider notes:

- `LLM_PROVIDER=mock` runs offline without credentials.
- `LLM_PROVIDER=openai` requires `LLM_API_KEY` and uses `LLM_MODEL`.
- `LLM_PROVIDER=gemini` requires `LLM_API_KEY` and uses `LLM_MODEL`.
- `LLM_BASE_URL` is optional and intended for OpenAI-compatible endpoints.

CORS is configured through `cors_allow_origins` in `backend/app/config.py`.
The current default is permissive for development. For deployment, restrict it
to the frontend origin when the hosting environment supports that setting.

## Local Development

Backend:

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --app-dir .
```

Frontend:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```
