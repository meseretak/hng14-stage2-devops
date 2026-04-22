import redis
import os
import sys

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    password=os.environ.get("REDIS_PASSWORD", None),
)
try:
    r.ping()
    sys.exit(0)
except Exception:
    sys.exit(1)
