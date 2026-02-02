import redis.asyncio as redis
from app.core.config import settings

class RedisManager:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            decode_responses=True
        )

    def get_client(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.pool)

redis_manager = RedisManager()