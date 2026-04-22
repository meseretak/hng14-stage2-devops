# syntax=docker/dockerfile:1
FROM python:3.12-alpine AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- final stage ----
FROM python:3.12-alpine

# Upgrade all OS packages to patch known CVEs
RUN apk upgrade --no-cache

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --from=builder /install /usr/local
COPY worker.py healthcheck.py ./

USER appuser

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "healthcheck.py"]

CMD ["python", "worker.py"]
