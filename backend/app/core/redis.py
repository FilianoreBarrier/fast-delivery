import os
from redis.asyncio import Redis, from_url

REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6379/0")

redis_client: Redis = from_url(
    REDIS_URL,
    encoding = "utf-8",
    decode_responses = True
)

async def get_redis() -> Redis:
    return redis_client
