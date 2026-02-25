# QUASAR AI Backend

Production-oriented FastAPI backend for AI exam proctoring.

## Run locally with Docker

```bash
cp .env.example .env
docker compose up --build
```

API docs: `http://localhost:8000/docs`

## Database migrations

```bash
alembic upgrade head
```

## Test

```bash
pytest
```
