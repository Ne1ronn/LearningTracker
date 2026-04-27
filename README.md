# LearningTracker

A backend pet project for tracking study progress.

## Features

- User registration and authentication with JWT
- Daily learning entries
- Topics and goals
- Quizzes for revision
- Weekly and profile stats
- Telegram bot integration
- Celery background reminders

## Tech Stack

- Python 3.12 / FastAPI
- SQLAlchemy + PostgreSQL + Alembic
- Celery + Redis
- Aiogram
- Pytest
- Docker

## Run Locally

1. Create `.env` and `.env.docker`

2. Install dependencies:
```bash
   poetry install
```

3. Run migrations:
```bash
   poetry run alembic upgrade head
```

4. Start API:
```bash
   poetry run uvicorn main:app --reload
```

## Run With Docker

```bash
docker compose up --build
```

## Run Tests

```bash
poetry run pytest -q api/tests
```

## Project Structure

```
api/routers      — API endpoints
api/crud         — business logic and DB operations
models/          — SQLAlchemy models
schemas/         — Pydantic schemas
telegram_bot/    — Telegram bot
alembic/         — migrations
```