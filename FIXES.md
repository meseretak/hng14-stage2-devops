# FIXES.md

Bugs found and fixed in the starter repo.

---

**1. api/main.py line 9 — Redis host hardcoded**
- Was: `redis.Redis(host="localhost")`
- Fixed: read from `REDIS_HOST` env var, defaults to `"redis"`

**2. api/main.py line 9 — no Redis password**
- Was: no auth passed to Redis client
- Fixed: pass `REDIS_PASSWORD` env var to client

**3. api/main.py line 10 — wrong queue key name**
- Was: `r.lpush("job", ...)` but worker used `"jobs"`
- Fixed: standardised both to `"jobs"`

**4. api/main.py line 18 — 404 returned as 200**
- Was: `return {"error": "not found"}` with 200 status
- Fixed: `raise HTTPException(status_code=404)`

**5. api/.env — real credentials committed to repo**
- Was: `REDIS_PASSWORD=supersecretpassword123` in git
- Fixed: deleted file, added to .gitignore, added .env.example

**6. worker/worker.py line 6 — Redis host hardcoded**
- Was: `redis.Redis(host="localhost")`
- Fixed: read from `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` env vars

**7. worker/worker.py — no graceful shutdown**
- Was: no signal handling, killed mid-job on container stop
- Fixed: added SIGTERM/SIGINT handlers with clean exit

**8. frontend/app.js line 6 — API URL hardcoded**
- Was: `const API_URL = "http://localhost:8000"`
- Fixed: read from `API_URL` env var, defaults to `"http://api:8000"`

**9. frontend/app.js — no /health endpoint**
- Was: no health route, Docker HEALTHCHECK had nothing to call
- Fixed: added `GET /health` returning `{"status":"ok"}`

**10. frontend/app.js — error handler hides upstream status**
- Was: always returned 500 regardless of upstream error
- Fixed: propagate actual status code from API response

**11. api/requirements.txt — missing python-multipart, no pinned versions**
- Was: `fastapi`, `uvicorn`, `redis` unpinned, multipart missing
- Fixed: pinned all versions, added `python-multipart`

**12. frontend/package.json — no lint script or eslint config**
- Was: no eslint setup at all
- Fixed: added eslint dev dep, lint script, .eslintrc.json

**13. no .gitignore in repo**
- Was: nothing ignored, .env could be committed accidentally
- Fixed: added .gitignore covering Python, Node, Docker artifacts
