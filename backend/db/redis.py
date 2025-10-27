from redis.asyncio import Redis
from core.config import get_settings

JTI_EXPIRY = 3600
BLOCK_PREFIX = "jwt:blocklist:"

token_blocklist = Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    password=get_settings().REDIS_PASSWORD,
)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=f"{BLOCK_PREFIX}{jti}", value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    return await token_blocklist.exists(f"{BLOCK_PREFIX}{jti}") == 1