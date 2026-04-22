# HNG14 Stage 2 — Job Processing System

Three services: a Node.js frontend, a Python/FastAPI backend, and a Python worker. Redis is the queue between the API and worker.

## Stack

- Frontend — Node/Express, port 3000
- API — Python/FastAPI, port 8000
- Worker — Python, reads jobs from Redis queue
- Redis — internal only, not exposed to host

## Prerequisites

- Docker
- Docker Compose v2
- Git

## Run it locally

```bash
git clone https://github.com/meseretak/hng14-stage2-devops.git
cd hng14-stage2-devops
cp .env.example .env
# edit .env and set REDIS_PASSWORD
docker compose up --build -d
```

Open http://localhost:3000

## Check everything is running

```bash
docker compose ps
```

All four services should show as healthy/running.

## Stop

```bash
docker compose down
```

## Environment variables

| Variable | Used by | Default |
|---|---|---|
| REDIS_PASSWORD | all | — |
| REDIS_HOST | api, worker | redis |
| REDIS_PORT | api, worker | 6379 |
| API_URL | frontend | http://api:8000 |
| PORT | frontend | 3000 |
| FRONTEND_PORT | compose | 3000 |

## Run tests

```bash
pip install -r api/requirements.txt -r api/requirements-dev.txt
cd api && pytest tests/ --cov=. --cov-report=term-missing
```

## CI/CD pipeline

Runs on every push. Stages in order:

1. Lint — flake8, eslint, hadolint
2. Test — pytest with mocked Redis, uploads coverage artifact
3. Build — builds all 3 images, tags with git SHA + latest
4. Security — Trivy scans all images, fails on CRITICAL OS CVEs
5. Integration — spins up full stack, submits a job, polls until completed
6. Deploy — SSH rolling update to production server (main branch only)

## Live app

http://136.115.145.233:3000
