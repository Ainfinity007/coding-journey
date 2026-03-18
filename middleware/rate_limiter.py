"""
Rate limiting middleware using Redis sliding window algorithm.
Implements per-IP and per-user rate limiting for FastAPI endpoints.
"""
import time
import os
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis

RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "100"))
RATE_LIMIT_WINDOW = 60  # seconds

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True,
        )
    return _redis_client


def _check_rate_limit(key: str, limit: int, window: int = RATE_LIMIT_WINDOW) -> tuple[int, int]:
    """
    Sliding window rate limit check using Redis sorted sets.
    Returns (current_count, limit).
    Raises HTTPException 429 if limit exceeded.
    """
    r = get_redis()
    now = time.time()
    window_start = now - window

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    results = pipe.execute()
    current_count = results[2]

    if current_count > limit:
        reset_time = int(now) + window
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down.",
                "details": {
                    "limit": limit,
                    "window_seconds": window,
                    "retry_after": window,
                },
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(window),
            },
        )
    return current_count, limit


async def ip_rate_limit_middleware(request: Request, call_next):
    """Middleware: rate limits by client IP address."""
    client_ip = request.client.host if request.client else "unknown"
    # Skip rate limiting for health checks
    if request.url.path in ("/health", "/metrics"):
        return await call_next(request)

    key = f"rate_limit:ip:{client_ip}"
    count, limit = _check_rate_limit(key, RATE_LIMIT_RPM)

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
    return response


def user_rate_limit(limit: int = 1000):
    """Dependency: rate limits by authenticated user ID."""
    security = HTTPBearer(auto_error=False)

    async def _check(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        if credentials is None:
            return  # unauthenticated requests handled by IP limit
        # Extract user_id from token (simplified; use proper JWT decode in production)
        token = credentials.credentials
        user_id = token[:16]  # placeholder — replace with JWT decode
        key = f"rate_limit:user:{user_id}"
        _check_rate_limit(key, limit)

    return _check
