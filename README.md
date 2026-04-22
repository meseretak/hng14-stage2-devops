# HNG14 Stage 2 — Containerised Job Processing System

A multi-service job processing application containerised with Docker and shipped via a full CI/CD pipeline on GitHub Actions.

## Architecture

```
Browser → Frontend (Node/Express :3000)
              ↓ HTTP
          API (FastAPI :8000)
              ↓ Redis queue
          Worker (Python)
              ↑
           Redis (internal only)
```

All services communicate over a private Docker bridge network. Redis is never exposed on the host.

---

## Prerequisites

- Docker >= 24.x
- Docker Compose plugin (`docker compose` v2)
- Git

---

## Quick Start (from scratch)

### 1. Clone your fork

```bash
git clone https://github.com/<your-username>/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and set a strong `REDIS_PASSWORD`:

```env
REDIS_PASSWORD=your_strong_password_here
FRONTEND_PORT=3000
```

### 3. Build and start the stack

```bash
docker compose up --build -d
```

### 4. Verify everything is running

```bash
docker compose ps
```

Expected output — all services should show `healthy` or `running`:

```
NAME         STATUS          PORTS
redis        Up (healthy)
api          Up (healthy)
worker       Up
frontend     Up              0.0.0.0:3000->3000/tcp
```

### 5. Open the dashboard

Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

Click "Submit New Job" — you should see the job appear with status `queued`, then transition to `completed` within a few seconds.

---

## Stopping the stack

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```

---

## Running Tests Locally

```bash
pip install -r api/requirements.txt -r api/requirements-dev.txt
PYTHONPATH=api pytest api/tests/ --cov=api --cov-report=term-missing
```

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and PR with these stages in strict order:

| Stage | What it does |
|---|---|
| lint | flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| test | pytest with Redis mocked, uploads coverage artifact |
| build | Builds all 3 images, tags with git SHA + latest, pushes to local registry |
| security | Trivy scans all images, fails on CRITICAL CVEs, uploads SARIF |
| integration | Brings full stack up, submits a job, polls until completed, tears down |
| deploy | Rolling update on `main` push only — new container must pass health check within 60s |

### Required GitHub Secrets (for deploy stage)

| Secret | Description |
|---|---|
| `DEPLOY_HOST` | IP or hostname of your production server |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_KEY` | Private SSH key (the server must have the public key in `authorized_keys`) |
| `REDIS_PASSWORD` | Redis password used in production |

---

## Environment Variables Reference

| Variable | Service | Description | Default |
|---|---|---|---|
| `REDIS_HOST` | api, worker | Redis hostname | `redis` |
| `REDIS_PORT` | api, worker | Redis port | `6379` |
| `REDIS_PASSWORD` | api, worker, redis | Redis auth password | — |
| `API_URL` | frontend | Internal URL of the API | `http://api:8000` |
| `PORT` | frontend | Port the frontend listens on | `3000` |
| `FRONTEND_PORT` | compose | Host port mapped to frontend | `3000` |
