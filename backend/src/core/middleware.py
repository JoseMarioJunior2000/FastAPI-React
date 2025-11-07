from fastapi import FastAPI, Request
from src.db.redis import redis_client
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings
from redis.asyncio import Redis
from uuid import UUID, uuid4
import time

class RateLimiter:
    def __init__(self, redis_client: Redis, max_requests=10, window=60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window

    async def allow_request(self, user_id) -> bool:
        now = time.time()
        key = f"rate_limit:{user_id}"

        member = f"{now}-{uuid4()}"

        pipe = self.redis.pipeline()
        pipe.zadd(key, {member: now})
        pipe.zremrangebyscore(key, 0, now - self.window)
        pipe.zcard(key)
        pipe.expire(key, int(self.window * 2))

        _, _, request_count, _ = await pipe.execute()

        allowed = request_count <= self.max_requests
        if not allowed:
            await self.redis.zrem(key, member)
        return allowed