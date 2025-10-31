from redis.asyncio import Redis
from core.config import get_settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

JTI_EXPIRY = 3600
BLOCK_PREFIX = "jwt:blocklist:"

redis_client = Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    password=get_settings().REDIS_PASSWORD,
)

async def add_jti_to_blocklist(jti: str) -> None:
    await redis_client.set(name=f"{BLOCK_PREFIX}{jti}", value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    return await redis_client.exists(f"{BLOCK_PREFIX}{jti}") == 1