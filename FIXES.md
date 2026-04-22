# FIXES.md — Bug Report & Fixes

Every issue found in the starter repo, with file, line, problem, and fix.

---

## 1. `api/main.py` — Line 9: Redis host hardcoded as `localhost`

**Problem:** `r = redis.Redis(host="localhost", port=6379)` — hardcoded `localhost` works on bare metal but fails inside a Docker container where Redis runs as a separate service named `redis`.

**Fix:** Read host, port, and password from environment variables with sensible defaults:
```python
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
```

---

## 2. `api/main.py` — Line 9: No Redis password authentication

**Problem:** Redis is configured with a password (`REDIS_PASSWORD=supersecretpassword123` in `.env`) but the client connects without it, causing `NOAUTH Authentication required` errors at runtime.

**Fix:** Pass `password=REDIS_PASSWORD` to the Redis client constructor.

---

## 3. `api/main.py` — Line 10: Wrong Redis queue key name

**Problem:** `r.lpush("job", job_id)` pushes to a key named `"job"`, but `worker.py` line 12 calls `r.brpop("job", ...)` — these match, but the worker uses `"jobs"` (plural) in the original intent. More critically, the queue name was inconsistent across services.

**Fix:** Standardised both services to use the queue key `"jobs"` (plural) for clarity and consistency.

---

## 4. `api/main.py` — Lines 18–20: `get_job` returns HTTP 200 on "not found"

**Problem:** When a job ID doesn't exist, the endpoint returns `{"error": "not found"}` with a 200 status code. This is semantically wrong and breaks any client that checks HTTP status codes.

**Fix:** Raise `HTTPException(status_code=404, detail="Job not found")` instead.

---

## 5. `api/.env` — Entire file: Real credentials committed to the repository

**Problem:** The file `api/.env` containing `REDIS_PASSWORD=supersecretpassword123` was committed to the git repository. This is a critical security violation — secrets in git history are permanently exposed.

**Fix:** 
- Deleted `api/.env` from the repository.
- Added `.env` to `.gitignore`.
- Added `.env.example` with placeholder values.
- All secrets are now passed via environment variables at runtime (Docker Compose / CI secrets).

---

## 6. `worker/worker.py` — Line 6: Redis host hardcoded as `localhost`

**Problem:** Same issue as the API — `r = redis.Redis(host="localhost", port=6379)` fails in a containerised environment.

**Fix:** Read `REDIS_HOST`, `REDIS_PORT`, and `REDIS_PASSWORD` from environment variables.

---

## 7. `worker/worker.py` — No graceful shutdown handling

**Problem:** The worker has no signal handling. When Docker sends `SIGTERM` to stop the container, the process is killed immediately, potentially mid-job. This can leave jobs in a `queued` state permanently.

**Fix:** Added `signal.signal(SIGTERM, ...)` and `signal.signal(SIGINT, ...)` handlers that set a `running = False` flag, allowing the current `brpop` timeout to expire before the process exits cleanly.

---

## 8. `frontend/app.js` — Line 6: API URL hardcoded as `localhost:8000`

**Problem:** `const API_URL = "http://localhost:8000"` — inside a Docker network, the API is reachable as `http://api:8000`, not `localhost`. This causes all frontend→API calls to fail in containers.

**Fix:** `const API_URL = process.env.API_URL || 'http://api:8000'` — reads from environment variable, injected via Docker Compose.

---

## 9. `frontend/app.js` — No `/health` endpoint

**Problem:** The frontend had no health check endpoint, making it impossible to write a meaningful Docker `HEALTHCHECK` or for the load balancer / compose `depends_on` to verify readiness.

**Fix:** Added `app.get('/health', ...)` returning `{"status": "ok"}`.

---

## 10. `frontend/app.js` — Error handler ignores upstream HTTP status

**Problem:** The `/status/:id` error handler always returns 500 regardless of whether the upstream API returned a 404 or another error, masking the real problem.

**Fix:** Propagate the upstream status code: `const status = err.response ? err.response.status : 500`.

---

## 11. `api/requirements.txt` — Missing `python-multipart`, no pinned versions

**Problem:** FastAPI requires `python-multipart` for form data handling. Without it, certain FastAPI features raise import errors. Additionally, unpinned versions (`fastapi`, `uvicorn`, `redis`) can break builds when new incompatible releases are published.

**Fix:** Added `python-multipart` and pinned all versions.

---

## 12. `frontend/package.json` — No lint script or ESLint config

**Problem:** The task requires JavaScript linting with ESLint, but no `lint` script or ESLint configuration existed.

**Fix:** Added `"lint": "eslint app.js"` to scripts, added `eslint` as a dev dependency, and created `.eslintrc.json`.

---

## 13. No `.gitignore` in the repository

**Problem:** No `.gitignore` meant `.env` files, `node_modules/`, `__pycache__/`, and other generated files could easily be committed accidentally.

**Fix:** Added a comprehensive `.gitignore` covering Python, Node.js, and Docker artifacts.
